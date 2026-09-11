import discord

from discord.ext import commands
from discord import app_commands
from data.database import configure_guild


class Setup(commands.GroupCog, group_name="setup", description="Configure your server for War Games."):
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

        updated_role = interaction.guild.get_role(guild.host_role_id)
        updated_channel = interaction.guild.get_channel(guild.result_channel_id)

        if updated_role is None or updated_channel is None:

            embed = discord.Embed(
                title="War Games",
                description="That role or channel no longer exists in this server. Use `/setup server` to reconfigure the settings.",
                color=discord.Color.red()
            )

            return await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = discord.Embed(
            title="War Games",
            description=(f"The following settings have been updated in **{interaction.guild.name}**:\n\n"),
            color=discord.Color.green()
        )

        embed.add_field(name="Role assigned to hosts", value=f"{updated_role.mention}", inline=False)
        embed.add_field(name="Channel for results", value=f"{updated_channel.mention}", inline=False)

        await interaction.response.send_message(embed=embed)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))