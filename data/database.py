from __future__ import annotations
from datetime import datetime

from peewee import *
from playhouse.pwasyncio import AsyncSqliteDatabase

from data.enums import SeasonStatus

db = AsyncSqliteDatabase("db/war-games.db")


class SeasonStatusField(TextField):
    def db_value(self, value: SeasonStatus | str) -> str:
        return SeasonStatus(value).value

    def python_value(self, value: str) -> SeasonStatus:
        return SeasonStatus(value)

## Guild

class Guild(db.Model):
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

class Season(db.Model):
    name = TextField()
    team_size = IntegerField()
    starts_at = DateTimeField()
    status = SeasonStatusField(default=SeasonStatus.ACTIVE)
    guild = ForeignKeyField(Guild, backref="seasons")

    def __str__(self) -> str:
        return f"{self.name} • {self.starts_at:%b %Y}"


async def create_tables():
    async with db:
        await db.acreate_tables([Guild, Season], safe=True)
