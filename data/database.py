import asyncio
from peewee import *
from playhouse.pwasyncio import AsyncSqliteDatabase

db = AsyncSqliteDatabase("db/war-games.db")

class BaseModel(Model):
    class Meta:
        database = db

## Guild

class Guild(BaseModel):
    guild_id = IntegerField(primary_key=True)
    host_role_id = IntegerField(null=True)
    result_channel_id = IntegerField(null=True)

async def create_tables():
    async with db:
        await db.acreate_tables([Guild], safe=True)