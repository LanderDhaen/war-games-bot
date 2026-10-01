from asyncpg.exceptions import UniqueViolationError

from data.database import Phase
from data.enum import PhaseEnum
from errors.phase import DuplicatePhase


async def create_phase(
    tournament_id: int,
    phase: PhaseEnum,
) -> None:

    try:
        await Phase.insert(
            Phase(
                {
                    Phase.tournament: tournament_id,
                    Phase.format: phase,
                }
            )
        )
    except UniqueViolationError as error:
        if error.constraint_name == "unique_phase__format_tournament":
            raise DuplicatePhase(phase) from error
        raise