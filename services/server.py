from piccolo.query.methods.insert import OnConflictAction

from data.database import Configuration, Guild, utc_now
from errors.configs import MissingConfiguration


async def create_guild(guild_id: int) -> None:
    await Guild.insert(Guild(guild_id=guild_id)).on_conflict(
        target=Guild.guild_id,
        action=OnConflictAction.do_update,
        values=[
            Guild.modified_at,
            (Guild.joined_at, utc_now()),
            (Guild.left_at, None),
        ],
    )


async def remove_guild(guild_id: int) -> None:
    await Guild.update({Guild.left_at: utc_now()}).where(Guild.guild_id == guild_id)


async def configure_server(
    guild_id: int,
    host_role_id: int,
    participant_role_id: int,
    game_channel_id: int,
    results_channel_id: int,
) -> None:

    await Guild.insert(Guild(guild_id=guild_id)).on_conflict(
        target=Guild.guild_id,
        action=OnConflictAction.do_nothing,
    )

    await Configuration.insert(
        Configuration(
            {
                Configuration.guild: guild_id,
                Configuration.host_role_id: host_role_id,
                Configuration.participant_role_id: participant_role_id,
                Configuration.game_channel_id: game_channel_id,
                Configuration.results_channel_id: results_channel_id,
            }
        )
    ).on_conflict(
        target=Configuration.guild,
        action=OnConflictAction.do_update,
        values=[
            Configuration.modified_at,
            Configuration.host_role_id,
            Configuration.participant_role_id,
            Configuration.game_channel_id,
            Configuration.results_channel_id,
        ],
    )


async def get_configuration(guild_id: int) -> Configuration:
    configuration = await Configuration.objects().get(Configuration.guild == guild_id)

    if not configuration:
        raise MissingConfiguration()

    return configuration
