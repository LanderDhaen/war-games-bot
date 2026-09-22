import discord
from discord.ext import commands
from typing import Literal

from config import TOKEN


class WarGamesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)


bot = WarGamesBot()


@bot.command(name="sync")
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, scope: Literal["global", "guild"] = "guild"):
    if scope == "guild":
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"{len(synced)} command(s) synced for {ctx.guild.name}.")
    elif scope == "global":
        synced = await bot.tree.sync()
        await ctx.send(f"{len(synced)} command(s) synced globally.")


bot.run(TOKEN)
