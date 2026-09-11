from peewee import *
from playhouse.pwasyncio import AsyncSqliteDatabase

db = AsyncSqliteDatabase("db/war-games.db")

## Guild

class Guild(db.Model):
    guild_id = IntegerField(primary_key=True)
    host_role_id = IntegerField()
    result_channel_id = IntegerField()

async def get_guild(guild_id: int) -> Guild | None:
    return await Guild.aget_or_none(Guild.guild_id == guild_id)

async def configure_guild(guild_id: int, host_role_id: int, result_channel_id: int) -> Guild:

    guild = await get_guild(guild_id)

    if not guild:
        guild = await Guild.acreate(guild_id=guild_id, host_role_id=host_role_id, result_channel_id=result_channel_id)
    else:
        guild.host_role_id = host_role_id
        guild.result_channel_id = result_channel_id
        await guild.asave()

    return guild

async def create_tables():
    async with db:
        await db.acreate_tables([Guild], safe=True)