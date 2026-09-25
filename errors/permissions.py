from errors.base import ExpectedCheckFailure


class MissingPermission(ExpectedCheckFailure):
    """Raised when a user does not have the required permission(s)."""

    title = "Missing Permission"
    description = "You don't have permission to use this command."


class MissingAdministratorPermission(MissingPermission):
    """Raised when a user does not have Administrator permission."""

    description = "You need to be an administrator to use this command."
