import discord
from datetime import datetime
from discord.ext import commands
from discord import app_commands

from core.checks import get_guild_config, requires_host
from core.errors import InvalidSeasonStart

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
    async def schedule_season(self, interaction: discord.Interaction, name: str, team_size: discord.app_commands.Range[int, 1], starts_at: str):

        if interaction.guild is None:
            raise app_commands.NoPrivateMessage()

        guild = await get_guild_config(interaction.guild)

        try:
            parsed_starts_at = datetime.fromisoformat(starts_at)
        except ValueError:
            raise InvalidSeasonStart() from None

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

async def setup(bot: commands.Bot):
    await bot.add_cog(Season(bot))

