from asyncpg.exceptions import UniqueViolationError

from data.database import Tournament
from errors.tournaments import DuplicateTournament


async def create_tournament(
    guild_id: int,
    name: str,
    description: str | None = None,
) -> None:
    try:
        await Tournament.insert(
            Tournament(
                {
                    Tournament.guild: guild_id,
                    Tournament.name: name,
                    Tournament.description: description,
                }
            )
        )
    except UniqueViolationError as error:
        if error.constraint_name == "unique_tournament_name_guild":
            raise DuplicateTournament(name) from error
        raise
