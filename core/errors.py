from discord import app_commands


class MissingGuildConfiguration(app_commands.CheckFailure):
    pass


class MissingHostRole(app_commands.CheckFailure):
    pass


class InvalidGuildConfiguration(app_commands.AppCommandError):
    pass


class InvalidSeasonStart(app_commands.AppCommandError):
    pass
