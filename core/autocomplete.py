import discord
from discord import app_commands

from services.tournament import get_tournaments


async def tournament_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:

    guild = interaction.guild
    if guild is None:
        return []

    tournaments = await get_tournaments(guild.id)
    current = current.casefold()

    return [
        app_commands.Choice(name=tournament.name, value=tournament.name)
        for tournament in tournaments
        if current in tournament.name.casefold()
    ][:25]
