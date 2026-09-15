from enum import StrEnum


class SeasonStatus(StrEnum):
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"

    def __str__(self) -> str:
        return self.name.title()
