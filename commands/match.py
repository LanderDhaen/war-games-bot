from contextlib import suppress

import discord
from asyncpg.exceptions import ForeignKeyViolationError
from discord import app_commands
from discord.ext import commands

from core.autocomplete import (
    active_season_autocomplete,
    match_team_b_autocomplete,
    season_team_autocomplete,
)
from core.checks import get_guild, get_interaction_guild, requires_host
from core.errors import (
    EmptyMatchTeam,
    InvalidMatchConfiguration,
    MatchThreadCreationFailed,
    MissingResultsChannelConfiguration,
    SeasonNotFound,
    TeamNotFound,
    TeamsMustBeDifferent,
)


@app_commands.guild_only()
class Match(
    commands.GroupCog, group_name="match", description="Manage matches for War Games."
):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="schedule", description="Schedule a match between two teams."
    )
    @app_commands.describe(
        season_code="The season where the match will be played.",
        team_a_code="The first team.",
        team_b_code="The second team.",
    )
    @app_commands.rename(
        season_code="season",
        team_a_code="team-a",
        team_b_code="team-b",
    )
    @app_commands.autocomplete(
        season_code=active_season_autocomplete,
        team_a_code=season_team_autocomplete,
        team_b_code=match_team_b_autocomplete,
    )
    @requires_host()
    async def schedule_match(
        self,
        interaction: discord.Interaction,
        season_code: str,
        team_a_code: str,
        team_b_code: str,
    ):
        server = get_interaction_guild(interaction)

        await interaction.response.defer()

        guild = await get_guild(server.id)

        channel = server.get_channel(guild.results_channel_id)

        if channel is None:
            try:
                channel = await server.fetch_channel(guild.results_channel_id)
            except discord.NotFound:
                raise MissingResultsChannelConfiguration()

        if not isinstance(channel, discord.TextChannel):
            raise MissingResultsChannelConfiguration()

        season = await guild.get_active_season_by_code(season_code)
        team_a = await season.get_team_by_code(team_a_code)

        if not team_a:
            raise TeamNotFound()

        team_b = await season.get_team_by_code(team_b_code)

        if not team_b:
            raise TeamNotFound()

        if team_a.id == team_b.id:
            raise TeamsMustBeDifferent()

        team_a_memberships = await team_a.get_members()
        team_b_memberships = await team_b.get_members()

        if not team_a_memberships or not team_b_memberships:
            raise EmptyMatchTeam()

        try:
            thread = await channel.create_thread(
                name=f"{team_a.name} vs {team_b.name}",
                auto_archive_duration=10080,
                type=discord.ChannelType.private_thread,
            )
        except discord.HTTPException:
            raise MatchThreadCreationFailed()

        try:
            await season.schedule_match(team_a, team_b, thread.id)
        except ForeignKeyViolationError:
            with suppress(discord.HTTPException):
                await thread.delete()

            raise InvalidMatchConfiguration() from None
        except Exception:
            with suppress(discord.HTTPException):
                await thread.delete()

            raise

        thread_message_content = " ".join(
            f"<@{membership.user_id}>"
            for membership in team_a_memberships + team_b_memberships
        )

        thread_embed = discord.Embed(
            title="Match Information",
            description=f"The following match has been scheduled in **{season}**.",
            color=discord.Color.blue(),
        )

        thread_embed.add_field(name="Team A", value=team_a.name, inline=True)
        thread_embed.add_field(
            name="Players",
            value="\n".join(
                f"• <@{membership.user_id}>" for membership in team_a_memberships
            ),
            inline=True,
        )
        thread_embed.add_field(
            name="\u200b", value="\u200b", inline=True
        )  # Add a blank field for spacing

        thread_embed.add_field(name="Team B", value=team_b.name, inline=True)
        thread_embed.add_field(
            name="Players",
            value="\n".join(
                f"• <@{membership.user_id}>" for membership in team_b_memberships
            ),
            inline=True,
        )
        thread_embed.add_field(
            name="\u200b", value="\u200b", inline=True
        )  # Add a blank field for spacing

        await thread.send(content=thread_message_content, embed=thread_embed)

        embed = discord.Embed(
            title="Match Scheduled",
            description=(
                f"**{team_a.name}** vs **{team_b.name}** has been "
                f"scheduled for **{season}** in {thread.mention}"
            ),
            color=discord.Color.green(),
        )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Match(bot))
