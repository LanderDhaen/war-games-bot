from data.database import Guild
from errors.configs import MissingConfiguration
from piccolo.query.methods.insert import OnConflictAction


async def configure_server(
    guild_id: int,
    host_role_id: int,
    participant_role_id: int,
    game_channel_id: int,
    results_channel_id: int,
) -> None:

    await Guild.insert(
        Guild(
            {
                Guild.guild_id: guild_id,
                Guild.host_role_id: host_role_id,
                Guild.participant_role_id: participant_role_id,
                Guild.game_channel_id: game_channel_id,
                Guild.results_channel_id: results_channel_id,
            }
        )
    ).on_conflict(
        target=Guild.guild_id,
        action=OnConflictAction.do_update,
        values=[
            Guild.modified_at,
            Guild.host_role_id,
            Guild.participant_role_id,
            Guild.game_channel_id,
            Guild.results_channel_id,
        ],
    )


async def get_configuration(guild_id: int) -> Guild:
    guild = await Guild.objects().get(Guild.guild_id == guild_id)

    if not guild:
        raise MissingConfiguration()

    return guild
