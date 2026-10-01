from errors.base import ExpectedError



class DuplicatePhase(ExpectedError):
    """Raised when a phase is already in use in a tournament."""

    title = "Duplicate Phase"

    def __init__(self, phase_name: str):
        self.description = (
            f"A phase with the name `{phase_name}` already exists in this tournament."
        )
        super().__init__()



