from discord import app_commands


class WarGamesError(Exception):
    title: str
    message: str

    def __init__(self):
        super().__init__(self.message)


class MissingGuildConfiguration(WarGamesError, app_commands.CheckFailure):
    title = "Missing Configuration"
    message = (
        "This server is not yet configured. "
        "An administrator can use `/setup server` to get started."
    )


class MissingHostRole(WarGamesError, app_commands.CheckFailure):
    title = "Missing Permission"
    message = "You need to be a host to use this command."


class InvalidGuildConfiguration(WarGamesError, app_commands.AppCommandError):
    title = "Invalid Configuration"
    message = (
        "That role or channel no longer exists in this server. "
        "Use `/setup server` to reconfigure the settings."
    )


class InvalidSeasonStart(WarGamesError, app_commands.AppCommandError):
    title = "Invalid Configuration"
    message = (
        "This is not a valid date and time. Please use the ISO format, "
        "for example `2026-09-20 19:00`."
    )
