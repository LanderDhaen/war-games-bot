import discord
from discord import app_commands
from discord.ext import commands

from core.checks import requires_host
from core.context import get_interaction_guild
from services.tournament import create_tournament


class Tournament(
    commands.GroupCog, group_name="tournament", description="Manage tournaments of War Games."
):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add", description="Add a new tournament of War Games.")
    @app_commands.describe(
        name="The name of the tournament.", description="The description of the tournament."
    )
    @app_commands.guild_only()
    @requires_host()
    async def setup_tournament(
        self,
        interaction: discord.Interaction,
        name: discord.app_commands.Range[str, 1, 90],
        description: str | None = None,
    ) -> None:

        await interaction.response.defer()

        guild = get_interaction_guild(interaction)

        await create_tournament(guild.id, name, description)

        await interaction.followup.send("Tournament created successfully.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tournament(bot))
