from errors.base import ExpectedError


class InvalidTournamentName(ExpectedError):
    """Raised when a tournament name is empty after normalisation."""

    title = "Invalid Tournament"
    description = "A tournament name must contain at least one visible character."


class DuplicateTournament(ExpectedError):
    """Raised when a tournament name is already in use in a server."""

    title = "Duplicate Tournament"

    def __init__(self, tournament_name: str):
        self.description = (
            f"A tournament with the name `{tournament_name}` already exists in this server."
        )
        super().__init__()


class MissingTournament(ExpectedError):
    """Raised when a tournament can't be found in the current server."""

    title = "Missing Tournament"

    def __init__(self, tournament_name: str):
        self.description = (
            f"A tournament with the name `{tournament_name}` doesn't exist in this server."
        )
        super().__init__()
