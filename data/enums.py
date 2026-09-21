from enum import StrEnum


class SeasonStatus(StrEnum):
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"


class MatchStatus(StrEnum):
    OPEN = "OPEN"


class PhaseName(StrEnum):
    LEAGUE = "LEAGUE"
    ROUND_OF_512 = "ROUND OF 512"
    ROUND_OF_256 = "ROUND OF 256"
    ROUND_OF_128 = "ROUND OF 128"
    ROUND_OF_64 = "ROUND OF 64"
    ROUND_OF_32 = "ROUND OF 32"
    ROUND_OF_16 = "ROUND OF 16"
    QUARTER_FINALS = "QUARTER FINALS"
    SEMI_FINALS = "SEMI FINALS"
    FINAL = "FINAL"
    THIRD_PLACE = "THIRD PLACE"
