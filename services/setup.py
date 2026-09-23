from piccolo.query.methods.insert import OnConflictAction

from data.database import Guild


async def configure_server(
    guild_id: int,
    host_role_id: int,
    participant_role_id: int,
    game_channel_id: int,
    results_channel_id: int,
) -> Guild:

    guild = await Guild.objects().get_or_create(
        Guild.guild_id == guild_id,
        defaults={
            Guild.host_role_id: host_role_id,
            Guild.participant_role_id: participant_role_id,
            Guild.game_channel_id: game_channel_id,
            Guild.results_channel_id: results_channel_id,
        },
    )

    if guild._was_created:
        return guild

    guild.update_self(
        {
            Guild.host_role_id: host_role_id,
            Guild.participant_role_id: participant_role_id,
            Guild.game_channel_id: game_channel_id,
            Guild.results_channel_id: results_channel_id,
        }
    )

    return guild
