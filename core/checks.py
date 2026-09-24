import discord
from discord import app_commands

from errors.permissions import MissingAdministratorPermission


def requires_admin():
    def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.permissions.administrator:
            raise MissingAdministratorPermission()
        return True

    return app_commands.check(predicate)
