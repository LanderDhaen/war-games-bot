import discord

from discord import app_commands
from data.database import get_guild
from data.enums import SeasonStatus

async def active_season_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[int]]:

    server = interaction.guild

    if server is None:
        raise app_commands.NoPrivateMessage()
    
    guild = await get_guild(server.id)
    seasons = await guild.get_active_seasons()

    return [
        app_commands.Choice(name=str(season)[:100], value=season.id)
        for season in seasons
        if current.casefold() in str(season).casefold()
    ][:25]


async def season_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[int]]:

    server = interaction.guild

    if server is None:
        raise app_commands.NoPrivateMessage()
    
    guild = await get_guild(server.id)
    seasons = await guild.get_seasons()

    return [
        app_commands.Choice(name=str(season)[:100], value=season.id)
        for season in seasons
        if current.casefold() in str(season).casefold()
    ][:25]


async def season_team_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[int]]:

    server = interaction.guild

    if server is None:
        raise app_commands.NoPrivateMessage()
    
    season_id = getattr(interaction.namespace, "season", None)

    if not isinstance(season_id, int):
        return []

    guild = await get_guild(server.id)
    season = await guild.get_season_by_id(season_id)

    if not season or season.status == SeasonStatus.FINISHED:
        return []

    teams = await season.get_teams()

    return [
        app_commands.Choice(name=str(team)[:100], value=team.id)
        for team in teams
        if current.casefold() in str(team).casefold()
    ][:25]


async def match_team_b_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[int]]:

    server = interaction.guild

    if server is None:
        raise app_commands.NoPrivateMessage()

    season_id = getattr(interaction.namespace, "season", None)

    if not isinstance(season_id, int):
        return []

    team_a_id = getattr(interaction.namespace, "team-a", None)
    guild = await get_guild(server.id)
    season = await guild.get_season_by_id(season_id)

    if season is None or season.status == SeasonStatus.FINISHED:
        return []

    teams = await season.get_teams()

    return [
        app_commands.Choice(name=str(team)[:100], value=team.id)
        for team in teams
        if team.id != team_a_id
        and current.casefold() in str(team).casefold()
    ][:25]
