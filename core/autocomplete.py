import discord

from discord import app_commands

from core.checks import get_guild_config


async def active_season_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[int]]:
    guild = await get_guild_config(interaction.guild)
    seasons = await guild.get_active_seasons()

    return [
        app_commands.Choice(name=str(season)[:100], value=season.id)
        for season in seasons
        if current.casefold() in season.name.casefold()
    ][:25]


async def season_team_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[int]]:
    season_id = getattr(interaction.namespace, "season", None)

    if not isinstance(season_id, int):
        return []

    guild = await get_guild_config(interaction.guild)
    season = await guild.get_active_season(season_id)

    if season is None:
        return []

    teams = await season.get_teams()

    return [
        app_commands.Choice(name=team.name[:100], value=team.id)
        for team in teams
        if current.casefold() in team.name.casefold()
    ][:25]
