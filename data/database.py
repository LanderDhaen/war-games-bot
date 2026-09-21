from __future__ import annotations

from datetime import datetime, timezone

from piccolo.table import Table, create_db_tables
from piccolo.columns import OnDelete, Serial, ForeignKey, Text, Integer, Timestamptz, Varchar
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.constraints import Check, Unique

from core.errors import MissingGuildConfiguration, SeasonNotFound
from data.enums import SeasonStatus, MatchStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class BaseTable(Table):
    id = Serial(primary_key=True)
    created_at = Timestamptz(default=TimestamptzNow())
    modified_at = Timestamptz(default=TimestamptzNow(), auto_update=utc_now)

class Guild(BaseTable):
    guild_id = Integer(unique=True)
    host_role_id = Integer(unique=True)
    participant_role_id = Integer(unique=True)
    game_channel_id = Integer(unique=True)
    results_channel_id = Integer(unique=True)

    async def start_season(self, name: str, team_size: int, starts_at: datetime) -> Season:
        season = Season(
            name=name,
            team_size=team_size,
            starts_at=starts_at,
            guild=self,
        )
        await season.save()

        return season

    async def finish_season(self, season_id: int) -> Season:
        season = await self.get_season_by_id(season_id)

        season.status = SeasonStatus.FINISHED

        await season.save()

        return season

    async def get_seasons(self) -> list[Season]:
        return await Season.objects().where(Season.guild == self).order_by(Season.starts_at, ascending=False)

    async def get_active_seasons(self) -> list[Season]:
        return await Season.objects().where(Season.guild == self and Season.status == SeasonStatus.ACTIVE).order_by(Season.starts_at, ascending=False)

    async def get_season_by_id(self, season_id: int) -> Season:

        season = await Season.objects().where(Season.id == season_id).first()

        if season is None:
            raise SeasonNotFound()
        
        return season


class Season(BaseTable):
    name = Varchar(length=100)
    team_size = Integer()
    starts_at = Timestamptz(default=TimestamptzNow())
    status = Text(default=SeasonStatus.ACTIVE, choices=SeasonStatus)
    guild = ForeignKey(references=Guild, on_delete=OnDelete.cascade)

    def __str__(self) -> str:
        return f"{self.name} • {self.starts_at.strftime("%B %Y")}"

    async def get_teams(self) -> list[Team]:
        return await Team.objects().where(Team.season == self).order_by(Team.name)

class Team(BaseTable):
    name = Varchar(length=100)
    season = ForeignKey(references=Season, on_delete=OnDelete.cascade)

class TeamMember(BaseTable):
    user_id = Integer()
    season = ForeignKey(references=Season, on_delete=OnDelete.cascade)
    team = ForeignKey(references=Team, on_delete=OnDelete.cascade)

class Match(BaseTable):
    season = ForeignKey(references=Season, on_delete=OnDelete.cascade)
    team_a = ForeignKey(references=Team, on_delete=OnDelete.restrict)
    team_b = ForeignKey(references=Team, on_delete=OnDelete.restrict)
    thread_id = Integer(null=True)
    status = Text(default=MatchStatus.OPEN, choices=MatchStatus)

async def configure_guild(guild_id: int, host_role_id: int, participant_role_id: int, game_channel_id: int, results_channel_id: int):

    guild = await Guild.objects().where(Guild.guild_id == guild_id).first()

    if guild:
        guild.host_role_id = host_role_id
        guild.participant_role_id = participant_role_id
        guild.game_channel_id = game_channel_id
        guild.results_channel_id = results_channel_id
        await guild.save()

        created = False

    else:
        guild = Guild(
            guild_id=guild_id,
            host_role_id=host_role_id,
            participant_role_id=participant_role_id,
            results_channel_id=results_channel_id,
        )
        await guild.save()
        created = True


    return guild, created

async def get_guild(guild_id: int) -> Guild:
    guild = await Guild.objects().where(Guild.guild_id == guild_id).first()

    if not guild:
        raise MissingGuildConfiguration()

    return guild

async def create_tables() -> None:
    await create_db_tables(Guild, Season, Team, TeamMember, Match, if_not_exists=True)