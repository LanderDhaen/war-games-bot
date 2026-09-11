import discord

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
    @app_commands.check(host_only)
    async def schedule_season(self, interaction: discord.Interaction, name: str):

        guild = await get_guild(interaction.guild.id)

        if not guild:
            isAdmin = interaction.user.guild_permissions.administrator

            embed = discord.Embed(
                title="Missing configuration",
                description="Your server is not not yet configured. Use `/setup server` to get started." if isAdmin else "This server is not yet configured. Please contact an administrator.",
                color=discord.Color.red()
            )

            return await interaction.response.send_message(embed=embed, ephemeral=True)

        season = await guild.create_season(name)

        embed = discord.Embed(
            title="Season scheduled",
            description=f"{season.name} has been scheduled for **{interaction.guild.name}**.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Season(bot))

