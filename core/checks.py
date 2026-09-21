import discord
from discord import app_commands

from core.errors import (
    MissingHostRole,
    MissingHostRoleConfiguration,
)
from data.database import get_guild


def get_interaction_guild(interaction: discord.Interaction) -> discord.Guild:
    guild = interaction.guild

    if guild is None:
        raise app_commands.NoPrivateMessage()

    return guild


def requires_config():
    async def predicate(interaction: discord.Interaction) -> bool:
        discord_guild = get_interaction_guild(interaction)

        await get_guild(discord_guild)
        
        return True

    return app_commands.check(predicate)


def requires_host():
    async def predicate(interaction: discord.Interaction) -> bool:
        server = get_interaction_guild(interaction)

        guild = await get_guild(server.id)
        host_role = server.get_role(guild.host_role_id)

        if host_role is None:
            try:
                host_role = await server.fetch_role(guild.host_role_id)
            except discord.NotFound:
                raise MissingHostRoleConfiguration()

        if host_role not in interaction.user.roles:
            raise MissingHostRole()

        return True

    return app_commands.check(predicate)
