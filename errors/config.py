from errors.base import ExpectedError


class MissingConfiguration(ExpectedError):
    """Raised when a server does not have the required configuration to use a command."""

    title = "Missing Configuration"
    description = "This server is not yet configured. An administrator can use `/server configure` to get started."


class MissingHostRoleConfiguration(MissingConfiguration):
    """Raised when a server does not have a host role configured."""

    description = "The configured host role doesn't exist. An administrator can use `/server configure` to reconfigure it."


class MissingParticipantRoleConfiguration(MissingConfiguration):
    """Raised when a server does not have a participant role configured."""

    description = "The configured participant role doesn't exist. An administrator can use `/server configure` to reconfigure it."


class MissingGameChannelConfiguration(MissingConfiguration):
    """Raised when a server does not have a game channel configured."""

    description = "The configured game channel doesn't exist. An administrator can use `/server configure` to reconfigure it."


class MissingResultsChannelConfiguration(MissingConfiguration):
    """Raised when a server does not have a results channel configured."""

    description = "The configured results channel doesn't exist. An administrator can use `/server configure` to reconfigure it."
