from discord import Guild, Interaction, Role, TextChannel, app_commands

from errors.configs import (
    MissingGameChannelConfiguration,
    MissingHostRoleConfiguration,
    MissingParticipantRoleConfiguration,
    MissingResultsChannelConfiguration,
)


def get_interaction_guild(interaction: Interaction) -> Guild:

    guild = interaction.guild

    if guild is None:
        raise app_commands.NoPrivateMessage()

    return guild


def get_host_role(guild: Guild, role_id: int) -> Role:

    role = guild.get_role(role_id)

    if role is None:
        raise MissingHostRoleConfiguration()

    return role


def get_participant_role(guild: Guild, role_id: int) -> Role:

    role = guild.get_role(role_id)

    if role is None:
        raise MissingParticipantRoleConfiguration()

    return role


def get_game_channel(guild: Guild, channel_id: int) -> TextChannel:

    channel = guild.get_channel(channel_id)

    if not isinstance(channel, TextChannel):
        raise MissingGameChannelConfiguration()

    return channel


def get_results_channel(guild: Guild, channel_id: int) -> TextChannel:

    channel = guild.get_channel(channel_id)

    if not isinstance(channel, TextChannel):
        raise MissingResultsChannelConfiguration()

    return channel
