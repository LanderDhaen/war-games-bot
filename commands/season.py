import discord
from datetime import datetime
from discord.ext import commands
from discord import app_commands

from core.autocomplete import active_season_autocomplete, season_autocomplete
from core.checks import requires_host
from core.errors import (
    InvalidSeasonName,
    InvalidSeasonStart,
    InvalidSeasonTeamSize,
    SeasonNotFound,
)
from data.enums import SeasonStatus

from data.database import get_guild

@app_commands.guild_only()
class Season(commands.GroupCog, group_name="season", description="Manage seasons for War Games."):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="schedule", description="Schedule a new season of War Games.")
    @app_commands.describe(name="The name of the season to schedule.")
    @app_commands.describe(team_size="The number of players in a team.")
    @app_commands.describe(raw_starts_at="The season start in ISO format, for example 2026-09-20 19:00.")
    @app_commands.rename(team_size="team-size")
    @app_commands.rename(raw_starts_at="starts-at")
    @requires_host()
    async def schedule_season(
        self,
        interaction: discord.Interaction,
        name: app_commands.Range[str, 1, 100],
        team_size: app_commands.Range[int, 1, 5],
        raw_starts_at: str,
    ):

        server = interaction.guild

        if not server:
            raise app_commands.NoPrivateMessage()

        guild = await get_guild(server.id)

        name = name.strip()

        if not 1 <= len(name) <= 100:
            raise InvalidSeasonName()

        if not 1 <= team_size <= 5:
            raise InvalidSeasonTeamSize()

        try:
            starts_at = datetime.fromisoformat(raw_starts_at)
        except ValueError:
            raise InvalidSeasonStart()

        season = await guild.start_season(name, team_size, starts_at)

        embed = discord.Embed(
            title="Season Scheduled",
            description=f"A new War Games season has been scheduled in **{server.name}**:",
            color=discord.Color.green()
        )

        embed.add_field(name="Name", value=str(season), inline=False)
        embed.add_field(name="Format", value=f"{season.team_size} vs {season.team_size}", inline=False)
        embed.add_field(name="Starts", value=discord.utils.format_dt(season.starts_at), inline=False)


        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="Display information about a season of War Games.")
    @app_commands.describe(season_id="The season to display.")
    @app_commands.rename(season_id="season")
    @app_commands.autocomplete(season_id=season_autocomplete)
    async def season_info(
        self,
        interaction: discord.Interaction,
        season_id: int,
    ):  

        server = interaction.guild

        if server is None:
            raise app_commands.NoPrivateMessage()
        
        guild = await get_guild(server.id)
        season = await guild.get_season_by_id(season_id)

        if season is None:
            raise SeasonNotFound()

        teams = await season.get_teams()

        is_finished = season.status == SeasonStatus.FINISHED

        embed = discord.Embed(
            title="Season Information",
            description=f"The following season {('was hosted' if is_finished else 'is going on')} in **{server.name}**.",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Name", value=str(season), inline=False)
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
    @app_commands.describe(season_id="The season that should be updated.")
    @app_commands.rename(season_id="season")
    @app_commands.autocomplete(season_id=active_season_autocomplete)
    @requires_host()
    async def finish_season(
        self,
        interaction: discord.Interaction,
        season_id: int,
    ):
        server = interaction.guild

        if server is None:
            raise app_commands.NoPrivateMessage()

        guild = await get_guild(server.id)
        season = await guild.finish_season(season_id)

        embed = discord.Embed(
            title="Season Updated",
            description=f"The status of **{season}** has been changed to **Finished**.",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Season(bot))
