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
