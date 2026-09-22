from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from config import (
    SEASON_CODE_MAX_LENGTH,
    SEASON_CODE_MIN_LENGTH,
    SEASON_NAME_MAX_LENGTH,
    SEASON_NAME_MIN_LENGTH,
    SEASON_TEAM_SIZE_MAX,
    SEASON_TEAM_SIZE_MIN,
)
from core.autocomplete import active_season_autocomplete, season_autocomplete
from core.checks import get_interaction_guild, requires_host
from core.errors import (
    InvalidSeasonCode,
    InvalidSeasonName,
    InvalidSeasonStart,
    InvalidSeasonTeamSize,
    SeasonNotFound,
)
from data.database import get_guild
from data.enums import SeasonStatus


@app_commands.guild_only()
class Season(commands.GroupCog, group_name="season", description="Manage seasons for War Games."):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="schedule", description="Schedule a new season of War Games.")
    @app_commands.describe(name="The name of the season to schedule.")
    @app_commands.describe(code="The code for the season to schedule.")
    @app_commands.describe(team_size="The number of players in a team.")
    @app_commands.describe(
        raw_starts_at="The season start in ISO format, for example 2026-09-20 19:00."
    )
    @app_commands.rename(team_size="team-size")
    @app_commands.rename(raw_starts_at="starts-at")
    @requires_host()
    async def schedule_season(
        self,
        interaction: discord.Interaction,
        name: app_commands.Range[str, SEASON_NAME_MIN_LENGTH, SEASON_NAME_MAX_LENGTH],
        code: app_commands.Range[str, SEASON_CODE_MIN_LENGTH, SEASON_CODE_MAX_LENGTH],
        team_size: app_commands.Range[int, SEASON_TEAM_SIZE_MIN, SEASON_TEAM_SIZE_MAX],
        raw_starts_at: str,
    ):

        server = get_interaction_guild(interaction)

        guild = await get_guild(server.id)

        name = name.strip()

        if not SEASON_NAME_MIN_LENGTH <= len(name) <= SEASON_NAME_MAX_LENGTH:
            raise InvalidSeasonName()

        code = code.strip()

        if not SEASON_CODE_MIN_LENGTH <= len(code) <= SEASON_CODE_MAX_LENGTH:
            raise InvalidSeasonCode()

        if not SEASON_TEAM_SIZE_MIN <= team_size <= SEASON_TEAM_SIZE_MAX:
            raise InvalidSeasonTeamSize()

        try:
            starts_at = datetime.fromisoformat(raw_starts_at)
        except ValueError:
            raise InvalidSeasonStart() from None

        season = await guild.start_season(name, code, team_size, starts_at)

        embed = discord.Embed(
            title="Season Scheduled",
            description=f"A new War Games season has been scheduled in **{server.name}**:",
            color=discord.Color.green(),
        )

        embed.add_field(name="Name", value=str(season), inline=True)
        embed.add_field(name="Code", value=season.code, inline=True)
        embed.add_field(
            name="Format",
            value=f"{season.team_size} vs {season.team_size}",
            inline=False,
        )
        embed.add_field(
            name="Starts", value=discord.utils.format_dt(season.starts_at), inline=False
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="info", description="Display information about a season of War Games."
    )
    @app_commands.describe(season_code="The season to display.")
    @app_commands.rename(season_code="season")
    @app_commands.autocomplete(season_code=season_autocomplete)
    async def season_info(
        self,
        interaction: discord.Interaction,
        season_code: str,
    ):

        server = get_interaction_guild(interaction)

        guild = await get_guild(server.id)
        season = await guild.get_season_by_code(season_code)

        if season is None:
            raise SeasonNotFound()

        teams = await season.get_teams()

        is_finished = season.status == SeasonStatus.FINISHED

        embed = discord.Embed(
            title="Season Information",
            description=(
                f"The following season "
                f"{('was hosted' if is_finished else 'is going on')} in **{server.name}**."
            ),
            color=discord.Color.blue(),
        )
        embed.add_field(name="Name", value=str(season), inline=True)
        embed.add_field(name="Code", value=season.code, inline=True)
        embed.add_field(
            name="Format",
            value=f"{season.team_size} vs {season.team_size}",
            inline=False,
        )
        embed.add_field(
            name="Status",
            value=season.status.title(),
            inline=False,
        )
        embed.add_field(name="Teams", value=str(len(teams)), inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="finish", description="Finish an active season of War Games.")
    @app_commands.describe(season_code="The season that should be updated.")
    @app_commands.rename(season_code="season")
    @app_commands.autocomplete(season_code=active_season_autocomplete)
    @requires_host()
    async def finish_season(
        self,
        interaction: discord.Interaction,
        season_code: str,
    ):
        server = get_interaction_guild(interaction)

        guild = await get_guild(server.id)
        season = await guild.finish_season(season_code)

        embed = discord.Embed(
            title="Season Updated",
            description=f"The status of **{season}** has been changed to **Finished**.",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Season(bot))
