import discord
from discord import app_commands

from core.errors import (
    MissingGuildConfiguration,
    MissingHostRole,
    MissingHostRoleConfiguration,
)
from data.database import Guild as GuildConfig
from data.database import get_guild


async def get_guild_config(guild: discord.Guild) -> GuildConfig:
    config = await get_guild(guild.id)

    if config is None:
        raise MissingGuildConfiguration()

    return config


def requires_config():
    async def predicate(interaction: discord.Interaction) -> bool:

        discord_guild = interaction.guild

        if discord_guild is None:
            raise app_commands.NoPrivateMessage()

        await get_guild_config(discord_guild)
        return True

    return app_commands.check(predicate)


def requires_host():
    async def predicate(interaction: discord.Interaction) -> bool:
        discord_guild = interaction.guild

        if discord_guild is None:
            raise app_commands.NoPrivateMessage()

        guild = await get_guild_config(discord_guild)
        host_role = discord_guild.get_role(guild.host_role_id)

        if host_role is None:
            raise MissingHostRoleConfiguration()

        if (
            not isinstance(interaction.user, discord.Member)
            or host_role not in interaction.user.roles
        ):
            raise MissingHostRole()

        return True

    return app_commands.check(predicate)
