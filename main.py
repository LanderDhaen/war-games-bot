from typing import Literal

import discord

from discord import app_commands
from discord.ext import commands
from config import TOKEN, HOST_ROLE_ID
from data.database import configure_guild, create_tables, get_guild

class WarGamesBot(commands.Bot):
    def __init__(self):

        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await create_tables()
        await self.load_extension("commands.setup") 

bot = WarGamesBot()

@bot.command(name="sync")
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, scope: Literal["global", "guild"] = "guild"):
    if scope == "guild":
        bot.tree.copy_global_to(guild=ctx.guild)
        synced  = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"{len(synced)} command(s) synced for {ctx.guild.name}.")
    elif scope == "global":
        synced = await bot.tree.sync()
        await ctx.send(f"{len(synced)} command(s) synced globally.")

bot.run(TOKEN)

