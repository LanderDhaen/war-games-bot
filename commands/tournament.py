import discord
from discord import app_commands
from discord.ext import commands

from core.checks import requires_host
from core.context import get_interaction_guild
from services.tournament import (
    create_tournament,
    delete_tournament,
    get_tournament,
    get_tournaments,
)


class Tournament(commands.GroupCog, group_name="tournament", description="Manage tournaments"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add", description="Add a new tournament")
    @app_commands.describe(
        name="The name of the tournament.", description="The description of the tournament."
    )
    @app_commands.guild_only()
    @requires_host()
    async def setup_tournament(
        self,
        interaction: discord.Interaction,
        name: discord.app_commands.Range[str, 1, 90],
        description: str | None = None,
    ) -> None:

        await interaction.response.defer()

        guild = get_interaction_guild(interaction)

        await create_tournament(guild.id, name, description)

        embed = discord.Embed(
            title="Tournament Added",
            description=f"A new War Games tournament has been added in **{guild.name}**",
            color=discord.Color.green(),
        )

        embed.add_field(name="Name", value=name, inline=False)

        embed.add_field(
            name="Description",
            value=description if description else "*This tournament has no description.*",
            inline=False,
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="info", description="Display the information about a tournament")
    @app_commands.describe(tournament_name="The tournament to display.")
    @app_commands.rename(tournament_name="tournament")
    @app_commands.guild_only()
    async def display_tournament(
        self,
        interaction: discord.Interaction,
        tournament_name: str,
    ) -> None:
        await interaction.response.defer()

        guild = get_interaction_guild(interaction)
        tournament = await get_tournament(guild.id, tournament_name)

        embed = discord.Embed(
            title="Tournament Information",
            description=f"The following tournament is hosted in **{guild.name}**:",
            colour=discord.Colour.blue(),
        )
        embed.add_field(name="Name", value=tournament.name, inline=False)
        embed.add_field(
            name="Description",
            value=tournament.description or "*This tournament has no description.*",
            inline=False,
        )
        embed.add_field(
            name="Created",
            value=discord.utils.format_dt(tournament.created_at, style="D"),
            inline=False,
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="list", description="Display the tournaments in this server")
    @app_commands.guild_only()
    async def list_tournaments(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        guild = get_interaction_guild(interaction)
        tournaments = await get_tournaments(guild.id)

        if tournaments:
            embed_description = f"The following tournaments are hosted in **{guild.name}**:\n\n"
            embed_description += "\n".join(
                f"1. {discord.utils.escape_markdown(tournament.name)}"
                for tournament in tournaments
            )

        else:
            embed_description = f"There are currently no tournaments in **{guild.name}**.\n\n"
            embed_description += "Use `/tournament add` to create a new tournament."

        embed = discord.Embed(
            title="Tournament List", description=embed_description, colour=discord.Colour.blue()
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="delete", description="Delete a tournament")
    @app_commands.describe(tournament_name="The tournament to delete.")
    @app_commands.rename(tournament_name="tournament")
    @app_commands.guild_only()
    @requires_host()
    async def remove_tournament(
        self,
        interaction: discord.Interaction,
        tournament_name: str,
    ) -> None:
        await interaction.response.defer()

        guild = get_interaction_guild(interaction)
        await delete_tournament(guild.id, tournament_name)

        embed = discord.Embed(
            title="Tournament Deleted",
            description=f"**{tournament_name}** has been deleted from **{guild.name}**.",
            colour=discord.Colour.green(),
        )

        await interaction.followup.send(embed=embed)

    @display_tournament.autocomplete("tournament_name")
    @remove_tournament.autocomplete("tournament_name")
    async def tournament_autocomplete(
        self,
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


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tournament(bot))
