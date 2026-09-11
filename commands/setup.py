import discord

from discord.ext import commands
from discord import app_commands
from data.database import configure_guild


class Setup(commands.GroupCog, group_name="setup", description="Configure your server for DL War Games."):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="server", description="Configure your server for War Games.")
    @app_commands.describe(host_role="The role that will be assigned to hosts.", result_channel="The channel where game results will be posted.")
    @app_commands.rename(host_role="host-role", result_channel="result-channel")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def setup_server(self, interaction: discord.Interaction, host_role: discord.Role, result_channel: discord.TextChannel):

        guild = await configure_guild(interaction.guild.id, host_role.id, result_channel.id)

        await interaction.response.send_message(f"Setting up your server for War Games with host role {guild.host_role_id} and result channel {guild.result_channel_id}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))