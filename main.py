import logging
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from config import TOKEN
from errors.base import ExpectedError
from services.server import create_guild, remove_guild

logger = logging.getLogger(__name__)


class WarGamesCommandTree(app_commands.CommandTree):
    async def on_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        match error:
            case ExpectedError():
                title = error.title
                description = error.description

            case app_commands.NoPrivateMessage():
                title = "What happened here?"
                description = (
                    f"`/{interaction.command.qualified_name}` cannot be used in private messages."
                )

            case _:
                error = (
                    error.original if isinstance(error, app_commands.CommandInvokeError) else error
                )

                title = "What happened here?"
                description = (
                    f"Something went wrong while executing `/{interaction.command.qualified_name}`."
                )

                logger.error(description, exc_info=error)

        embed = discord.Embed(
            title=title,
            description=description,
            colour=discord.Colour.red(),
        )

        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.HTTPException:
            logger.exception("Failed to send application command error response")


class WarGamesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents, tree_cls=WarGamesCommandTree)

    async def setup_hook(self) -> None:
        await self.load_extension("commands.server")
        await self.load_extension("commands.tournament")


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


@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    await create_guild(guild.id)


@bot.event
async def on_guild_remove(guild: discord.Guild) -> None:
    await remove_guild(guild.id)


if __name__ == "__main__":
    bot.run(TOKEN)
