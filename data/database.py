from __future__ import annotations
from datetime import datetime

from peewee import *
from playhouse.pwasyncio import AsyncSqliteDatabase

from data.enums import MatchStatus, SeasonStatus

db = AsyncSqliteDatabase(
    "db/war-games.db",
    pragmas={
        "journal_mode": "wal",
        "foreign_keys": 1,
        "busy_timeout": 5_000,
    },
)


class SeasonStatusField(TextField):
    def db_value(self, value: SeasonStatus | str) -> str:
        return SeasonStatus(value).value

    def python_value(self, value: str) -> SeasonStatus:
        return SeasonStatus(value)


class MatchStatusField(TextField):
    def db_value(self, value: MatchStatus | str) -> str:
        return MatchStatus(value).value

    def python_value(self, value: str) -> MatchStatus:
        return MatchStatus(value)


class BaseModel(db.Model):
    pass


## Guild

class Guild(BaseModel):
    guild_id = IntegerField(primary_key=True)
    host_role_id = IntegerField()
    participant_role_id = IntegerField()
    results_channel_id = IntegerField()

    async def create_season(self, name: str, team_size: int, starts_at: datetime) -> Season:
        return await Season.acreate(
            name=name,
            team_size=team_size,
            starts_at=starts_at,
            status=SeasonStatus.ACTIVE,
            guild=self,
        )

    async def get_active_seasons(self) -> list[Season]:
        query = Season.select().where(
            (Season.guild == self) & (Season.status == SeasonStatus.ACTIVE)
        ).order_by(Season.starts_at.desc())

        return await db.list(query)

    async def get_seasons(self) -> list[Season]:
        query = (
            Season.select()
            .where(Season.guild == self)
            .order_by(Season.starts_at.desc())
        )
        return await db.list(query)

    async def get_active_season(self, season_id: int) -> Season | None:
        return await Season.aget_or_none(
            (Season.id == season_id)
            & (Season.guild == self)
            & (Season.status == SeasonStatus.ACTIVE)
        )

    async def get_season(self, season_id: int) -> Season | None:
        return await Season.aget_or_none(
            (Season.id == season_id)
            & (Season.guild == self)
        )

    async def finish_season(self, season_id: int) -> Season | None:
        query = (
            Season.update(status=SeasonStatus.FINISHED)
            .where(
                (Season.id == season_id)
                & (Season.guild == self)
                & (Season.status == SeasonStatus.ACTIVE)
            )
            .returning(Season)
        )

        seasons = await db.list(query)

        if not seasons:
            return None

        return seasons[0]

async def get_guild(guild_id: int) -> Guild | None:
    return await Guild.aget_or_none(Guild.guild_id == guild_id)

async def configure_guild(
    guild_id: int,
    host_role_id: int,
    participant_role_id: int,
    results_channel_id: int,
) -> Guild:

    guild = await get_guild(guild_id)

    if not guild:
        guild = await Guild.acreate(
            guild_id=guild_id,
            host_role_id=host_role_id,
            participant_role_id=participant_role_id,
            results_channel_id=results_channel_id,
        )
    else:
        guild.host_role_id = host_role_id
        guild.participant_role_id = participant_role_id
        guild.results_channel_id = results_channel_id
        await guild.asave()

    return guild

## Season

class Season(BaseModel):
    id = AutoField()
    name = CharField(max_length=100)
    team_size = IntegerField()
    starts_at = DateTimeField()
    status = SeasonStatusField(default=SeasonStatus.ACTIVE)
    guild = ForeignKeyField(Guild, backref="seasons", on_delete="CASCADE")

    def __str__(self) -> str:
        return f"{self.name} • {self.starts_at:%b %Y}"

    async def create_team(self, name: str) -> Team:
        return await Team.acreate(name=name, season=self)

    async def schedule_match(self, team_a: Team, team_b: Team, thread_id: int) -> Match:
        return await Match.acreate(
            season=self,
            team_a=team_a,
            team_b=team_b,
            status=MatchStatus.OPEN,
            thread_id=thread_id,
        )

    async def get_teams(self) -> list[Team]:
        query = Team.select().where(Team.season == self).order_by(Team.name)
        return await db.list(query)

    async def get_team(self, team_id: int) -> Team | None:
        return await Team.aget_or_none(
            (Team.id == team_id)
            & (Team.season == self)
        )

    async def has_player(self, user_id: int) -> bool:
        query = TeamMember.select().where(
            (TeamMember.season == self)
            & (TeamMember.user_id == user_id)
        )
        return await db.exists(query)

## Team

class Team(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, collation="NOCASE")
    season = ForeignKeyField(Season, backref="teams", on_delete="CASCADE")

    class Meta:
        indexes = (
            (("season", "name"), True),
            (("id", "season"), True),
        )

    async def get_member_count(self) -> int:
        query = TeamMember.select().where(TeamMember.team == self)
        return await db.count(query)

    async def get_members(self) -> list[TeamMember]:
        query = (
            TeamMember.select()
            .where(TeamMember.team == self)
            .order_by(TeamMember.id)
        )
        return await db.list(query)

    async def add_player(self, user_id: int) -> TeamMember:
        return await TeamMember.acreate(
            season_id=self.season_id,
            team=self,
            user_id=user_id,
        )

    async def remove_player(self, user_id: int) -> TeamMember | None:
        query = (
            TeamMember.delete()
            .where(
                (TeamMember.season == self.season_id)
                & (TeamMember.team == self)
                & (TeamMember.user_id == user_id)
            )
            .returning(TeamMember)
        )
        members = await db.list(query)
        return members[0] if members else None

## Team Member

class TeamMember(BaseModel):
    id = AutoField()
    user_id = BigIntegerField()
    season = ForeignKeyField(Season, backref="members", on_delete="CASCADE")
    team = ForeignKeyField(Team, backref="members", on_delete="CASCADE")

    class Meta:
        indexes = (
            (("season", "user_id"), True),
        )


## Match

class Match(BaseModel):
    id = AutoField()
    season = ForeignKeyField(Season, backref="matches", on_delete="CASCADE")
    team_a = ForeignKeyField(Team, backref="matches_as_team_a", on_delete="RESTRICT")
    team_b = ForeignKeyField(Team, backref="matches_as_team_b", on_delete="RESTRICT")
    thread_id = BigIntegerField(null=True)
    status = MatchStatusField(default=MatchStatus.OPEN)

    class Meta:
        constraints = [
            SQL(
                'FOREIGN KEY ("team_a_id", "season_id") '
                'REFERENCES "team" ("id", "season_id")'
            ),
            SQL(
                'FOREIGN KEY ("team_b_id", "season_id") '
                'REFERENCES "team" ("id", "season_id")'
            ),
        ]

async def create_tables():
    async with db:
        await db.acreate_tables([Guild, Season, Team, TeamMember, Match], safe=True)
