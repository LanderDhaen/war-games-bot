from data.database import Guild
from errors.configs import MissingConfiguration


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

    await guild.update_self(
        {
            Guild.host_role_id: host_role_id,
            Guild.participant_role_id: participant_role_id,
            Guild.game_channel_id: game_channel_id,
            Guild.results_channel_id: results_channel_id,
        }
    )

    return guild


async def get_configuration(guild_id: int) -> Guild:
    guild = await Guild.objects().get(Guild.guild_id == guild_id)

    if not guild:
        raise MissingConfiguration()

    return guild
