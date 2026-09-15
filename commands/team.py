import discord

from discord import app_commands
from discord.ext import commands
from peewee import IntegrityError

from core.autocomplete import active_season_autocomplete, season_team_autocomplete
from core.checks import get_guild_config, requires_host
from core.errors import InvalidSeasonConfiguration, InvalidTeamConfiguration


@app_commands.guild_only()
class Team(commands.GroupCog, group_name="team", description="Manage teams for War Games."):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create", description="Create a new team for a season of War Games.")
    @app_commands.describe(
        season_id="The season where the team will participate.",
        name="The name of the team to create.",
    )
    @app_commands.rename(season_id="season")
    @app_commands.autocomplete(season_id=active_season_autocomplete)
    @requires_host()
    async def create_team(
        self,
        interaction: discord.Interaction,
        season_id: int,
        name: app_commands.Range[str, 1, 100],
    ):
        guild = await get_guild_config(interaction.guild)
        season = await guild.get_active_season(season_id)

        if season is None:
            raise InvalidSeasonConfiguration(
                "There's no active season with this ID."
            )

        name = name.strip()

        if not 1 <= len(name) <= 100:
            raise InvalidTeamConfiguration(
                "The team name must contain between 1 and 100 characters."
            )

        try:
            team = await season.create_team(name)
        except IntegrityError:
            raise InvalidTeamConfiguration(
                "A team with this name already exists in this season."
            ) from None

        embed = discord.Embed(
            title="Team Created",
            description=f"A new team has been created for **{season}**.",
            color=discord.Color.green(),
        )

        embed.add_field(name="Name", value=team.name, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="delete", description="Delete a team from a season of War Games.")
    @app_commands.describe(
        season_id="The season the team participates in.",
        team_id="The name of the team to delete.",
    )
    @app_commands.rename(season_id="season", team_id="team")
    @app_commands.autocomplete(
        season_id=active_season_autocomplete,
        team_id=season_team_autocomplete,
    )
    @requires_host()
    async def delete_team(
        self,
        interaction: discord.Interaction,
        season_id: int,
        team_id: int,
    ):
        guild = await get_guild_config(interaction.guild)
        season = await guild.get_active_season(season_id)

        if season is None:
            raise InvalidSeasonConfiguration(
                "There's no active season with this ID."
            )

        deleted_team = await season.delete_team(team_id)

        if deleted_team is None:
            raise InvalidTeamConfiguration(
                "There's no team with this ID in this season."
            )

        embed = discord.Embed(
            title="Team Deleted",
            description=f"**{deleted_team.name}** has been deleted from **{season}**.",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Team(bot))
