from errors.base import ExpectedError


class DuplicateTournament(ExpectedError):
    """Raised when a tournament name is already in use in a server."""

    title = "Duplicate Tournament"

    def __init__(self, tournament_name: str):
        self.description = (
            f"A tournament with the name `{tournament_name}` already exists in this server."
        )
        super().__init__()
