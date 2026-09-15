from typing import Literal

import discord

from discord import app_commands
from discord.ext import commands
from config import TOKEN
from core.errors import WarGamesError
from data.database import create_tables

class WarGamesBot(commands.Bot):
    def __init__(self):

        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await create_tables()
        await self.load_extension("commands.setup") 
        await self.load_extension("commands.season")

bot = WarGamesBot()


async def send_error_embed(
    interaction: discord.Interaction,
    embed: discord.Embed,
) -> None:
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.error
async def tree_on_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
):
    if isinstance(error, WarGamesError):
        embed = discord.Embed(
            title=error.title,
            description=error.message,
            color=discord.Color.red(),
        )
        await send_error_embed(interaction, embed)
    else:
        raise error

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

