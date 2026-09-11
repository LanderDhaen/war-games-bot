from __future__ import annotations
from peewee import *
from playhouse.pwasyncio import AsyncSqliteDatabase

db = AsyncSqliteDatabase("db/war-games.db")

## Guild

class Guild(db.Model):
    guild_id = IntegerField(primary_key=True)
    code = TextField(unique=True)
    host_role_id = IntegerField()
    result_channel_id = IntegerField()

    async def create_season(self, name: str, team_size: int) -> Season:
        return await Season.acreate(name=name, team_size = team_size, guild=self)

async def get_guild(guild_id: int) -> Guild | None:
    return await Guild.aget_or_none(Guild.guild_id == guild_id)

async def is_guild_code_available(code: str) -> bool:
    return await Guild.aget_or_none(Guild.code == code) is None

async def configure_guild(guild_id: int, code: str, host_role_id: int, result_channel_id: int) -> Guild:

    guild = await get_guild(guild_id)

    if not guild:
        guild = await Guild.acreate(guild_id=guild_id, code=code, host_role_id=host_role_id, result_channel_id=result_channel_id)
    else:
        guild.code = code
        guild.host_role_id = host_role_id
        guild.result_channel_id = result_channel_id
        await guild.asave()

    return guild

## Season

class Season(db.Model):
    name = CharField()
    team_size = IntegerField()
    guild = ForeignKeyField(Guild, backref="seasons")


async def create_tables():
    async with db:
        await db.acreate_tables([Guild, Season], safe=True)