import discord
from discord import app_commands
from discord.ext import commands

from core.autocomplete import (
    active_season_autocomplete,
    phase_name_autocomplete,
    season_phase_autocomplete,
)
from core.checks import get_interaction_guild, requires_host
from core.errors import InvalidPhaseName
from data.database import get_guild
from data.enums import PhaseName


@app_commands.guild_only()
class Phase(commands.GroupCog, group_name="phase", description="Manage tournament phases."):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="schedule", description="Schedule a phase for an active season.")
    @app_commands.describe(
        season_code="The season where the phase will be scheduled.",
        phase_name="The phase to schedule.",
    )
    @app_commands.rename(season_code="season", phase_name="name")
    @app_commands.autocomplete(
        season_code=active_season_autocomplete,
        phase_name=phase_name_autocomplete,
    )
    @requires_host()
    async def schedule_phase(
        self,
        interaction: discord.Interaction,
        season_code: str,
        phase_name: str,
    ):
        server = get_interaction_guild(interaction)

        guild = await get_guild(server.id)
        season = await guild.get_active_season_by_code(season_code)

        try:
            name = PhaseName(phase_name)
        except ValueError:
            raise InvalidPhaseName() from None

        phase = await season.schedule_phase(name)

        embed = discord.Embed(
            title="Phase Scheduled",
            description=f"**{phase}** has been scheduled for **{season}**.",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="delete", description="Delete a phase from an active season.")
    @app_commands.describe(
        season_code="The season the phase belongs to.",
        phase_name="The phase to delete.",
    )
    @app_commands.rename(season_code="season", phase_name="name")
    @app_commands.autocomplete(
        season_code=active_season_autocomplete,
        phase_name=season_phase_autocomplete,
    )
    @requires_host()
    async def delete_phase(
        self,
        interaction: discord.Interaction,
        season_code: str,
        phase_name: str,
    ):
        server = get_interaction_guild(interaction)

        guild = await get_guild(server.id)
        season = await guild.get_active_season_by_code(season_code)

        try:
            name = PhaseName(phase_name)
        except ValueError:
            raise InvalidPhaseName() from None

        phase = await season.delete_phase(name)

        embed = discord.Embed(
            title="Phase Deleted",
            description=f"**{phase}** has been deleted from **{season}**.",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Phase(bot))
