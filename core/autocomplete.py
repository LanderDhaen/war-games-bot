import discord
from discord import app_commands

from core.checks import get_interaction_guild
from data.database import get_guild
from data.enums import PhaseName, SeasonStatus


async def phase_name_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    del interaction

    return [
        app_commands.Choice(name=str(phase_name), value=phase_name)
        for phase_name in PhaseName
        if current.casefold() in phase_name.casefold()
    ][:25]


async def active_season_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:

    server = get_interaction_guild(interaction)

    guild = await get_guild(server.id)
    seasons = await guild.get_active_seasons()

    return [
        app_commands.Choice(name=str(season)[:100], value=season.code)
        for season in seasons
        if current.casefold() in str(season).casefold()
        or current.casefold() in season.code.casefold()
    ][:25]


async def season_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:

    server = get_interaction_guild(interaction)

    guild = await get_guild(server.id)
    seasons = await guild.get_seasons()

    return [
        app_commands.Choice(name=str(season)[:100], value=season.code)
        for season in seasons
        if current.casefold() in str(season).casefold()
        or current.casefold() in season.code.casefold()
    ][:25]


async def season_team_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:

    server = get_interaction_guild(interaction)

    season_code = getattr(interaction.namespace, "season", None)

    if not isinstance(season_code, str):
        return []

    guild = await get_guild(server.id)
    season = await guild.get_season_by_code(season_code)

    if not season or season.status == SeasonStatus.FINISHED:
        return []

    teams = await season.get_teams()

    return [
        app_commands.Choice(name=str(team)[:100], value=team.code)
        for team in teams
        if current.casefold() in str(team).casefold() or current.casefold() in team.code.casefold()
    ][:25]


async def match_team_b_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:

    server = get_interaction_guild(interaction)

    season_code = getattr(interaction.namespace, "season", None)

    if not isinstance(season_code, str):
        return []

    team_a_code = getattr(interaction.namespace, "team-a", None)
    guild = await get_guild(server.id)
    season = await guild.get_season_by_code(season_code)

    if season is None or season.status == SeasonStatus.FINISHED:
        return []

    teams = await season.get_teams()

    return [
        app_commands.Choice(name=str(team)[:100], value=team.code)
        for team in teams
        if team.code != team_a_code
        and (
            current.casefold() in str(team).casefold() or current.casefold() in team.code.casefold()
        )
    ][:25]
