import discord
from discord import app_commands
from discord.ext import commands

from core.checks import requires_admin
from services.setup import configure_server


class Setup(
    commands.GroupCog, group_name="setup", description="Configure your server for War Games."
):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="server", description="Configure your server for War Games.")
    @app_commands.describe(
        host_role="The role that will be assigned to hosts.",
        participant_role="The role that will be assigned to participants.",
        game_channel="The channel where games will be posted.",
        results_channel="The channel where game results will be posted.",
    )
    @app_commands.rename(
        host_role="host-role",
        participant_role="participant-role",
        game_channel="game-channel",
        results_channel="results-channel",
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    @requires_admin()
    async def setup_server(
        self,
        interaction: discord.Interaction,
        host_role: discord.Role,
        participant_role: discord.Role,
        game_channel: discord.TextChannel,
        results_channel: discord.TextChannel,
    ) -> None:
        server = interaction.guild

        if server is None:
            raise app_commands.NoPrivateMessage()

        guild = await configure_server(
            guild_id=server.id,
            host_role_id=host_role.id,
            participant_role_id=participant_role.id,
            game_channel_id=game_channel.id,
            results_channel_id=results_channel.id,
        )

        embed = discord.Embed(
            title="Server Configured",
            description=f"The following settings have been {('created' if guild._was_created else 'updated')} in **{server.name}**:",
            colour=discord.Colour.green(),
        )
        embed.add_field(
            name="The role that will be assigned to hosts.", value=host_role.mention, inline=False
        )
        embed.add_field(
            name="The role that will be assigned to participants.",
            value=participant_role.mention,
            inline=False,
        )
        embed.add_field(
            name="The channel where games will be posted.", value=game_channel.mention, inline=False
        )
        embed.add_field(
            name="The channel where game results will be posted.",
            value=results_channel.mention,
            inline=False,
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Setup(bot))
