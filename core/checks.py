import discord
from discord import app_commands

from core.context import get_host_role, get_interaction_guild
from errors.permissions import MissingAdministratorPermission, MissingHostPermission
from services.server import get_configuration


def requires_admin():
    def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.permissions.administrator:
            raise MissingAdministratorPermission()
        return True

    return app_commands.check(predicate)


def requires_host():
    async def predicate(interaction: discord.Interaction) -> bool:

        guild = get_interaction_guild(interaction)
        configuration = await get_configuration(guild.id)

        host_role = get_host_role(guild, configuration.host_role_id)

        if host_role not in interaction.user.roles:
            raise MissingHostPermission()

        return True

    return app_commands.check(predicate)
