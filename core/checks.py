import discord
from discord import app_commands

from core.errors import (
    MissingHostRole,
    MissingHostRoleConfiguration,
)
from data.database import get_configuration


def requires_config():
    async def predicate(interaction: discord.Interaction) -> bool:

        discord_guild = interaction.guild

        if discord_guild is None:
            raise app_commands.NoPrivateMessage()

        await get_configuration(discord_guild)
        
        return True

    return app_commands.check(predicate)


def requires_host():
    async def predicate(interaction: discord.Interaction) -> bool:
        discord_guild = interaction.guild

        if discord_guild is None:
            raise app_commands.NoPrivateMessage()

        guild = await get_configuration(discord_guild)
        host_role = discord_guild.get_role(guild.host_role_id)

        if host_role is None:
            raise MissingHostRoleConfiguration()

        if host_role not in interaction.user.roles:
            raise MissingHostRole()

        return True

    return app_commands.check(predicate)
