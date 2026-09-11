import discord

from discord.ext import commands
from discord import app_commands

from data.database import get_guild, is_season_code_available
from utils import slugify

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
    @app_commands.describe(code="The code that will be used to identify this season.")
    @app_commands.describe(team_size="The number of players in a team.")
    @app_commands.rename(team_size="team-size")
    @app_commands.check(host_only)
    async def schedule_season(self, interaction: discord.Interaction, name: str, code: str, team_size: discord.app_commands.Range[int, 1]):

        guild = await get_guild(interaction.guild.id)

        if not guild:
            is_admin = interaction.user.guild_permissions.administrator

            embed = discord.Embed(
                title="Missing Configuration",
                description="Your server is not not yet configured. Use `/setup server` to get started." if is_admin else "This server is not yet configured. Please contact an administrator.",
                color=discord.Color.red()
            )

            return await interaction.response.send_message(embed=embed, ephemeral=True)

        code = guild.code + "-" + slugify(code)

        is_available = await is_season_code_available(guild, code)

        if not is_available:
            embed = discord.Embed(
                title="Invalid Configuration",
                description=f"Another season is already using `{code}`. Please choose a different code.",
                color=discord.Color.red()
            )

            return await interaction.response.send_message(embed=embed, ephemeral=True)

        season = await guild.create_season(name, code, team_size)

        embed = discord.Embed(
            title="Season Scheduled",
            description=f"A new War Games season has been scheduled for **{interaction.guild.name}**:",
            color=discord.Color.green()
        )

        embed.add_field(name="Name used for the season", value=f"{season.name}", inline=False)
        embed.add_field(name="Code used to identify the season", value=f"`{season.code}`", inline=False)
        embed.add_field(name="Format used for the season", value=f"{season.team_size} vs {season.team_size}", inline=False)


        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Season(bot))

