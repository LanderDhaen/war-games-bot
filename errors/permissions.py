from discord.app_commands import CheckFailure


class MissingPermission(CheckFailure):
    """Raised when a user does not have the required permission(s)."""

    title = "Missing Permission"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class MissingAdministratorPermission(MissingPermission):
    """Raised when a user does not have Administrator permission."""

    def __init__(self):
        super().__init__(
            "You need to be an administrator to use this command."
        )