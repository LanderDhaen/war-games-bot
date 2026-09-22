import discord
from asyncpg.exceptions import UniqueViolationError
from discord import app_commands
from discord.ext import commands

from config import (
    TEAM_CODE_MAX_LENGTH,
    TEAM_CODE_MIN_LENGTH,
    TEAM_NAME_MAX_LENGTH,
    TEAM_NAME_MIN_LENGTH,
)
from core.autocomplete import (
    active_season_autocomplete,
    season_team_autocomplete,
)
from core.checks import get_interaction_guild, requires_host
from core.errors import (
    BotTeamMember,
    InvalidTeamCode,
    InvalidTeamName,
    MemberMissingParticipantRole,
    MissingParticipantRoleConfiguration,
    PlayerAddFailed,
    PlayerAlreadyAssigned,
    TeamFull,
    TeamNotFound,
)
from data.database import get_guild


@app_commands.guild_only()
class Team(commands.GroupCog, group_name="team", description="Manage teams for War Games."):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create", description="Create a new team for a season of War Games.")
    @app_commands.describe(
        season_code="The season where the team will participate.",
        name="The name of the team to create.",
        code="The code of the team to create.",
    )
    @app_commands.rename(season_code="season")
    @app_commands.autocomplete(season_code=active_season_autocomplete)
    @requires_host()
    async def create_team(
        self,
        interaction: discord.Interaction,
        season_code: str,
        name: app_commands.Range[str, TEAM_NAME_MIN_LENGTH, TEAM_NAME_MAX_LENGTH],
        code: app_commands.Range[str, TEAM_CODE_MIN_LENGTH, TEAM_CODE_MAX_LENGTH],
    ):

        server = get_interaction_guild(interaction)

        guild = await get_guild(server.id)
        season = await guild.get_active_season_by_code(season_code)

        name = name.strip()

        if not TEAM_NAME_MIN_LENGTH <= len(name) <= TEAM_NAME_MAX_LENGTH:
            raise InvalidTeamName()

        code = code.strip()

        if not TEAM_CODE_MIN_LENGTH <= len(code) <= TEAM_CODE_MAX_LENGTH:
            raise InvalidTeamCode()

        team = await season.create_team(name, code)

        embed = discord.Embed(
            title="Team Created",
            description=f"A new team has been created for **{season}**.",
            color=discord.Color.green(),
        )

        embed.add_field(name="Name", value=team.name, inline=True)
        embed.add_field(name="Code", value=team.code, inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="Display information about a team.")
    @app_commands.describe(
        season_code="The season the team participates in.",
        team_code="The team to display.",
    )
    @app_commands.rename(season_code="season", team_code="team")
    @app_commands.autocomplete(
        season_code=active_season_autocomplete,
        team_code=season_team_autocomplete,
    )
    async def team_info(
        self,
        interaction: discord.Interaction,
        season_code: str,
        team_code: str,
    ):

        server = get_interaction_guild(interaction)

        guild = await get_guild(server.id)
        season = await guild.get_active_season_by_code(season_code)

        team = await season.get_team_by_code(team_code)

        if team is None:
            raise TeamNotFound()

        members = await team.get_members()

        info_embed = discord.Embed(
            title="Team Information",
            description=f"The following team is participating in **{season}**.",
            color=discord.Color.blue(),
        )

        info_embed.add_field(name="Name", value=team.name, inline=True)
        info_embed.add_field(name="Code", value=team.code, inline=True)
        info_embed.add_field(
            name="Size",
            value=f"{len(members)}/{season.team_size}",
            inline=False,
        )

        players = (
            "\n".join(f"• <@{member.user_id}>" for member in members)
            or "*This team doesn't have any players.*"
        )
        info_embed.add_field(
            name="Players",
            value=players,
            inline=False,
        )

        await interaction.response.send_message(embed=info_embed)

    @app_commands.command(name="delete", description="Delete a team from a season of War Games.")
    @app_commands.describe(
        season_code="The season the team participates in.",
        team_code="The team to delete.",
    )
    @app_commands.rename(season_code="season", team_code="team")
    @app_commands.autocomplete(
        season_code=active_season_autocomplete,
        team_code=season_team_autocomplete,
    )
    @requires_host()
    async def delete_team(
        self,
        interaction: discord.Interaction,
        season_code: str,
        team_code: str,
    ):

        server = get_interaction_guild(interaction)

        guild = await get_guild(server.id)
        season = await guild.get_active_season_by_code(season_code)

        team = await season.get_team_by_code(team_code)

        team.remove()

        embed = discord.Embed(
            title="Team Deleted",
            description=f"**{team.name}** has been deleted from **{season}**.",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add-player", description="Add a player to a team.")
    @app_commands.describe(
        season_code="The season the team participates in.",
        team_code="The team to add the player to.",
        member="The name of the player to add.",
    )
    @app_commands.rename(season_code="season", team_code="team")
    @app_commands.autocomplete(
        season_code=active_season_autocomplete,
        team_code=season_team_autocomplete,
    )
    @requires_host()
    async def add_player(
        self,
        interaction: discord.Interaction,
        season_code: str,
        team_code: str,
        member: discord.Member,
    ):
        server = get_interaction_guild(interaction)

        if member.bot:
            raise BotTeamMember()

        guild = await get_guild(server.id)

        participant_role = server.get_role(guild.participant_role_id)

        if participant_role is None:
            try:
                participant_role = await server.fetch_role(guild.participant_role_id)
            except discord.NotFound:
                raise MissingParticipantRoleConfiguration() from None

        if participant_role not in member.roles:
            raise MemberMissingParticipantRole()

        season = await guild.get_active_season_by_code(season_code)

        if await season.has_player(member.id):
            raise PlayerAlreadyAssigned()

        team = await season.get_team_by_code(team_code)

        if await team.get_members_count() >= season.team_size:
            raise TeamFull()

        try:
            await team.add_member(member.id)
        except UniqueViolationError as error:
            if error.constraint_name in {
                "unique_team_member_season_user",
                "unique_team_member_team_user",
            }:
                raise PlayerAlreadyAssigned() from None
            raise PlayerAddFailed() from None

        embed = discord.Embed(
            title="Player Added",
            description=f"{member.mention} has been added to **{team.name}** for **{season}**.",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove-player", description="Remove a player from a team.")
    @app_commands.describe(
        season_code="The season the team participates in.",
        team_code="The team to remove the player from.",
        member="The name of the player to remove.",
    )
    @app_commands.rename(season_code="season", team_code="team")
    @app_commands.autocomplete(
        season_code=active_season_autocomplete,
        team_code=season_team_autocomplete,
    )
    @requires_host()
    async def remove_player(
        self,
        interaction: discord.Interaction,
        season_code: str,
        team_code: str,
        member: discord.Member,
    ):
        server = get_interaction_guild(interaction)

        guild = await get_guild(server.id)
        season = await guild.get_active_season_by_code(season_code)
        team = await season.get_team_by_code(team_code)

        await team.remove_member(member.id)

        embed = discord.Embed(
            title="Player Removed",
            description=f"{member.mention} has been removed from **{team.name}** for **{season}**.",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Team(bot))
