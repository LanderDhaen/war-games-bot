import discord
from datetime import datetime, timezone
from discord.ext import commands
from discord import app_commands

from core.autocomplete import active_season_autocomplete
from core.checks import get_guild_config, requires_host
from core.errors import InvalidSeasonConfiguration

@app_commands.guild_only()
class Season(commands.GroupCog, group_name="season", description="Manage seasons for War Games."):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="schedule", description="Schedule a new season for War Games.")
    @app_commands.describe(name="The name of the season to schedule.")
    @app_commands.describe(team_size="The number of players in a team.")
    @app_commands.describe(starts_at="The season start in ISO format, for example 2026-09-20 19:00.")
    @app_commands.rename(team_size="team-size")
    @app_commands.rename(starts_at="starts-at")
    @requires_host()
    async def schedule_season(
        self,
        interaction: discord.Interaction,
        name: app_commands.Range[str, 1, 100],
        team_size: app_commands.Range[int, 1, 50],
        starts_at: str,
    ):

        if interaction.guild is None:
            raise app_commands.NoPrivateMessage()

        guild = await get_guild_config(interaction.guild)

        name = name.strip()

        if not 1 <= len(name) <= 100:
            raise InvalidSeasonConfiguration(
                "The season name must contain between 1 and 100 characters."
            )

        if not 1 <= team_size <= 50:
            raise InvalidSeasonConfiguration(
                "The team size must be between 1 and 50 players."
            )

        try:
            parsed_starts_at = datetime.fromisoformat(starts_at)
        except ValueError:
            raise InvalidSeasonConfiguration(
                "This is not a valid date and time. Please use the ISO format, "
                "for example `2026-09-20 19:00`."
            ) from None

        if parsed_starts_at.tzinfo is None:
            parsed_starts_at = parsed_starts_at.replace(tzinfo=timezone.utc)
        else:
            parsed_starts_at = parsed_starts_at.astimezone(timezone.utc)

        season = await guild.create_season(name, team_size, parsed_starts_at)

        embed = discord.Embed(
            title="Season Scheduled",
            description=f"A new War Games season has been scheduled in **{interaction.guild.name}**:",
            color=discord.Color.green()
        )

        embed.add_field(name="Name", value=str(season), inline=False)
        embed.add_field(name="Format", value=f"{season.team_size} vs {season.team_size}", inline=False)
        embed.add_field(name="Starts", value=discord.utils.format_dt(season.starts_at), inline=False)


        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="finish", description="Finish an active season for War Games.")
    @app_commands.describe(season_id="The season that should be updated.")
    @app_commands.rename(season_id="season")
    @app_commands.autocomplete(season_id=active_season_autocomplete)
    @requires_host()
    async def finish_season(
        self,
        interaction: discord.Interaction,
        season_id: int,
    ):
        guild = await get_guild_config(interaction.guild)
        ended_season = await guild.finish_season(season_id)

        if ended_season is None:
            raise InvalidSeasonConfiguration(
                "There's no active season with this ID."
            )

        embed = discord.Embed(
            title="Season Updated",
            description=f"The status of **{ended_season}** has been changed to **Finished**.",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Season(bot))
