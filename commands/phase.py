import discord
from discord import app_commands
from discord.ext import commands

from core.autocomplete import tournament_autocomplete
from core.check import requires_host
from core.context import get_interaction_guild
from data.enum import PhaseEnum
from services.phase import create_phase
from services.tournament import get_tournament


class Phase(commands.GroupCog, group_name="phase", description="Manage phases"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="schedule", description="Schedule a new phase")
    @app_commands.describe(
        tournament_name="The name of the tournament.", phase="The phase to schedule."
    )
    @app_commands.rename(tournament_name="tournament")
    @app_commands.autocomplete(tournament_name=tournament_autocomplete)
    @app_commands.choices(phase=[app_commands.Choice(name=str(phase), value=phase.value) for phase in PhaseEnum])
    @app_commands.guild_only()
    @requires_host()
    async def schedule_phase(
        self,
        interaction: discord.Interaction,
        tournament_name: discord.app_commands.Range[str, 1, 90],
        phase: PhaseEnum
    ) -> None:

        await interaction.response.defer()

        guild = get_interaction_guild(interaction)
        tournament = await get_tournament(guild.id, tournament_name)

        await create_phase(
            tournament_id=tournament.id,
            phase=phase,
        )

        embed = discord.Embed(
            title="Phase Scheduled",
            description=f"The following phase has been scheduled in **{guild.name}**.",
            color=discord.Color.green(),
        )

        embed.add_field(name="Tournament", value=tournament.name, inline=True)
        embed.add_field(name="Phase", value=phase, inline=True)

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Phase(bot))
