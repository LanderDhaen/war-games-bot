import discord
from datetime import datetime

from discord.ext import commands
from discord import app_commands

from data.database import get_guild

async def host_only(interaction: discord.Interaction) -> bool:
    guild = await get_guild(interaction.guild.id)

    if not guild:
        return False

    host_role = interaction.guild.get_role(guild.host_role_id)

    if not host_role: 
        return False

    return host_role in interaction.user.roles

@app_commands.guild_only()
class Season(commands.GroupCog, group_name="season", description="Manage seasons for War Games."):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def interaction_check(self, interaction):
        return host_only(interaction)

    @app_commands.command(name="schedule", description="Schedule a new season for War Games.")
    @app_commands.describe(name="The name of the season to schedule.")
    @app_commands.describe(team_size="The number of players in a team.")
    @app_commands.describe(starts_at="The season start in ISO format, for example 2026-09-20 19:00.")
    @app_commands.rename(team_size="team-size")
    @app_commands.rename(starts_at="starts-at")
    @app_commands.check(host_only)
    async def schedule_season(self, interaction: discord.Interaction, name: str, team_size: discord.app_commands.Range[int, 1], starts_at: str):

        guild = await get_guild(interaction.guild.id)

        if not guild:
            is_admin = interaction.user.guild_permissions.administrator

            embed = discord.Embed(
                title="Missing Configuration",
                description="Your server is not not yet configured. Use `/setup server` to get started." if is_admin else "This server is not yet configured. Please contact an administrator.",
                color=discord.Color.red()
            )

            return await interaction.response.send_message(embed=embed, ephemeral=True)

        try:
            parsed_starts_at = datetime.fromisoformat(starts_at)
        except ValueError:
            embed = discord.Embed(
                title="Invalid Configuration",
                description="Use an ISO date and time, for example `2026-09-20 19:00`.",
                color=discord.Color.red()
            )

            return await interaction.response.send_message(embed=embed, ephemeral=True)

        season = await guild.create_season(name, team_size, parsed_starts_at)

        embed = discord.Embed(
            title="Season Scheduled",
            description=f"A new War Games season has been scheduled for **{interaction.guild.name}**:",
            color=discord.Color.green()
        )

        embed.add_field(name="Name used for the season", value=f"{season.name}", inline=False)
        embed.add_field(name="Format used for the season", value=f"{season.team_size} vs {season.team_size}", inline=False)
        embed.add_field(name="Starts at", value=discord.utils.format_dt(season.starts_at), inline=False)


        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Season(bot))

