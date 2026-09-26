from asyncpg.exceptions import UniqueViolationError

from data.database import Tournament
from errors.tournaments import DuplicateTournament, InvalidTournamentName, MissingTournament


async def create_tournament(
    guild_id: int,
    name: str,
    description: str | None = None,
) -> None:
    
    name = name.strip()

    if not name:
        raise InvalidTournamentName()

    if description is not None:
        description = description.strip() or None

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


async def get_tournament(guild_id: int, tournament_name: str) -> Tournament:
    tournament = await Tournament.objects().get(
        (Tournament.guild == guild_id) & (Tournament.name == tournament_name)
    )

    if tournament is None:
        raise MissingTournament(tournament_name)

    return tournament


async def get_tournaments(guild_id: int) -> list[Tournament]:
    return await Tournament.objects().where(Tournament.guild == guild_id).order_by(Tournament.name)
