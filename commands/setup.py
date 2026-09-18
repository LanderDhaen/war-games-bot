import discord

from discord.ext import commands
from discord import app_commands
from core.errors import (
    MissingGameChannelConfiguration,
    MissingHostRoleConfiguration,
    MissingParticipantRoleConfiguration,
    MissingResultsChannelConfiguration,
)
from data.database import configure_guild


class Setup(commands.GroupCog, group_name="setup", description="Configure your server for War Games."):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="server", description="Configure your server for War Games.")
    @app_commands.describe(host_role="The role that will be assigned to hosts.", participant_role="The role that will be assigned to participants.", game_channel="The channel where games will be posted.", results_channel="The channel where game results will be posted.")
    @app_commands.rename(host_role="host-role", participant_role="participant-role", game_channel="game-channel", results_channel="results-channel")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def setup_server(self, interaction: discord.Interaction, host_role: discord.Role, participant_role: discord.Role, game_channel: discord.TextChannel, results_channel: discord.TextChannel):
    
        if interaction.guild is None:
            raise app_commands.NoPrivateMessage()

        guild, created = await configure_guild(
            interaction.guild.id,
            host_role.id,
            participant_role.id,
            game_channel.id,
            results_channel.id,
        )

        updated_role = interaction.guild.get_role(guild.host_role_id)
        updated_participant_role = interaction.guild.get_role(guild.participant_role_id)
        updated_game_channel = interaction.guild.get_channel(guild.game_channel_id)
        updated_channel = interaction.guild.get_channel(guild.results_channel_id)
    
        if not updated_role:
            raise MissingHostRoleConfiguration()

        if not updated_participant_role:
            raise MissingParticipantRoleConfiguration()

        if not updated_game_channel:
            raise MissingGameChannelConfiguration()

        if not updated_channel:
            raise MissingResultsChannelConfiguration()

        embed = discord.Embed(
            title="Server Configured",
            description=(f"The following settings have been {('added' if created else 'updated')} in **{interaction.guild.name}**:\n\n"),
            color=discord.Color.green()
        )

        embed.add_field(name="The role that will be assigned to hosts.", value=f"{updated_role.mention}", inline=False)
        embed.add_field(name="The role that will be assigned to participants.", value=f"{updated_participant_role.mention}", inline=False)
        embed.add_field(name="The channel where games will be posted.", value=f"{updated_game_channel.mention}", inline=False)
        embed.add_field(name="The channel where game results will be posted.", value=f"{updated_channel.mention}", inline=False)

        await interaction.response.send_message(embed=embed)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
