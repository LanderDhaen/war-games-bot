from __future__ import annotations

from datetime import datetime, timezone

from asyncpg.exceptions import UniqueViolationError
from piccolo.table import Table, create_db_tables
from piccolo.columns import BigInt, OnDelete, Serial, ForeignKey, Text, Integer, Timestamptz, Varchar
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.constraints import Unique
from core.errors import DuplicateTeamName, MissingGuildConfiguration, PlayerNotInTeam, SeasonNotActive, SeasonNotFound, TeamNotFound
from data.enums import SeasonStatus, MatchStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class BaseTable(Table):
    id = Serial(primary_key=True)
    created_at = Timestamptz(default=TimestamptzNow())
    modified_at = Timestamptz(default=TimestamptzNow(), auto_update=utc_now)

class Guild(BaseTable):
    guild_id = BigInt(unique=True)
    host_role_id = BigInt(unique=True)
    participant_role_id = BigInt(unique=True)
    game_channel_id = BigInt(unique=True)
    results_channel_id = BigInt(unique=True)

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
        return await Season.objects().where((Season.guild == self) & (Season.status == SeasonStatus.ACTIVE)).order_by(Season.starts_at, ascending=False)

    async def get_season_by_id(self, season_id: int) -> Season:

        season = await Season.objects().where(Season.id == season_id).first()

        if season is None:
            raise SeasonNotFound()
        
        return season

    async def get_active_season_by_id(self, season_id: int) -> Season:

        season = await self.get_season_by_id(season_id)
        
        if season.status != SeasonStatus.ACTIVE:
            raise SeasonNotActive()

        return season

class Season(BaseTable):
    name = Varchar(length=100)
    team_size = Integer()
    starts_at = Timestamptz(default=TimestamptzNow())
    status = Text(default=SeasonStatus.ACTIVE, choices=SeasonStatus)
    guild = ForeignKey(references=Guild, on_delete=OnDelete.cascade)
    

    def __str__(self) -> str:
        return f"{self.name} • {self.starts_at.strftime("%B %Y")}"

    async def create_team(self, name: str) -> Team:
        team = Team(
            name=name,
            season=self,
        )

        try:
            await team.save()
        except UniqueViolationError:
            raise DuplicateTeamName() from None

        return team
        
    async def get_teams(self) -> list[Team]:
        return await Team.objects().where(Team.season == self).order_by(Team.name)

    async def get_team_by_id(self, team_id: int) -> Team:
        team = await Team.objects().where(Team.id == team_id).first()

        if team is None:
            raise TeamNotFound()

        return team

    async def has_player(self, user_id: int) -> bool:
        return await TeamMember.exists().where((TeamMember.season == self) & (TeamMember.user_id == user_id))

    async def schedule_match(self, team_a: Team, team_b: Team, thread_id: int) -> Match:
        match = Match(
            season=self,
            team_a=team_a,
            team_b=team_b,
            thread_id=thread_id,
        )

        await match.save()

        return match

class Team(BaseTable):
    name = Varchar(length=100)
    season = ForeignKey(references=Season)
    unique_name_season = Unique([name, season])

    def __str__(self) -> str:
        return self.name

    async def get_members(self) -> list[TeamMember]:
        return await TeamMember.objects().where(TeamMember.team == self).order_by(TeamMember.user_id)

    async def add_member(self, user_id: int) -> TeamMember:
        member = TeamMember(
            user_id=user_id,
            season=self.season,
            team=self,
        )
        await member.save()

        return member

    async def remove_member(self, user_id: int) -> TeamMember:
        member = await TeamMember.objects().where((TeamMember.team == self) & (TeamMember.user_id == user_id)).first()

        if member is None:
            raise PlayerNotInTeam()

        await member.remove()

        return member

    async def get_members_count(self) -> int:
        return await TeamMember.count().where(TeamMember.team == self)

class TeamMember(BaseTable):
    user_id = BigInt()
    season = ForeignKey(references=Season, on_delete=OnDelete.cascade)
    team = ForeignKey(references=Team, on_delete=OnDelete.cascade)

class Match(BaseTable):
    season = ForeignKey(references=Season, on_delete=OnDelete.cascade)
    team_a = ForeignKey(references=Team, on_delete=OnDelete.restrict)
    team_b = ForeignKey(references=Team, on_delete=OnDelete.restrict)
    thread_id = BigInt(null=True)
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
