from discord import app_commands


class WarGamesError(Exception):
    title: str
    message: str

    def __init__(self, description: str | None = None):
        if description is not None:
            self.message = description

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
    title = "Invalid Guild Configuration"
    message = "The guild configuration is invalid. Use `/setup server` to reconfigure the settings."


class InvalidSeasonConfiguration(WarGamesError, app_commands.AppCommandError):
    title = "Invalid Season Configuration"
    message = "The season configuration is invalid."


class InvalidTeamConfiguration(WarGamesError, app_commands.AppCommandError):
    title = "Invalid Team Configuration"
    message = "The team configuration is invalid."
