from discord.app_commands import AppCommandError


class MissingConfiguration(AppCommandError):
    """Raised when a server does not have the required configuration to use a command."""

    title = "Missing Configuration"

    def __init__(
        self,
        message: str = (
            "This server is not yet configured. An administrator can use "
            "`/server configure` to get started."
        ),
    ):
        self.message = message
        super().__init__(message)


class MissingHostRoleConfiguration(MissingConfiguration):
    """Raised when a server does not have a host role configured."""

    def __init__(self):
        super().__init__(
            "The configured host role doesn't exist. An administrator can use "
            "`/server configure` to reconfigure it."
        )


class MissingParticipantRoleConfiguration(MissingConfiguration):
    """Raised when a server does not have a participant role configured."""

    def __init__(self):
        super().__init__(
            "The configured participant role doesn't exist. An administrator can use "
            "`/server configure` to reconfigure it."
        )


class MissingGameChannelConfiguration(MissingConfiguration):
    """Raised when a server does not have a game channel configured."""

    def __init__(self):
        super().__init__(
            "The configured game channel doesn't exist. An administrator can use "
            "`/server configure` to reconfigure it."
        )


class MissingResultsChannelConfiguration(MissingConfiguration):
    """Raised when a server does not have a results channel configured."""

    def __init__(self):
        super().__init__(
            "The configured results channel doesn't exist. An administrator can use "
            "`/server configure` to reconfigure it."
        )
