from enum import StrEnum


class SeasonStatus(StrEnum):
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"


class MatchStatus(StrEnum):
    OPEN = "OPEN"


class PhaseName(StrEnum):
    LEAGUE = "League"
    ROUND_OF_512 = "Round of 512"
    ROUND_OF_256 = "Round of 256"
    ROUND_OF_128 = "Round of 128"
    ROUND_OF_64 = "Round of 64"
    ROUND_OF_32 = "Round of 32"
    ROUND_OF_16 = "Round of 16"
    QUARTER_FINALS = "Quarter Finals"
    SEMI_FINALS = "Semi Finals"
    FINAL = "Final"
    THIRD_PLACE = "Third Place"
