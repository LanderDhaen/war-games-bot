from enum import StrEnum, auto

class PhaseEnum(StrEnum):
    """An enumeration of the different phases in a tournament."""

    LEAGUE = auto()
    KNOCKOUT = auto()

    def __str__(self) -> str:
        return self.value.title()
