from __future__ import annotations

from datetime import UTC, datetime

from asyncpg.exceptions import (
    CheckViolationError,
    ForeignKeyViolationError,
    StringDataRightTruncationError,
    UniqueViolationError,
)
from piccolo.columns import (
    BigInt,
    ForeignKey,
    Integer,
    OnDelete,
    Serial,
    Text,
    Timestamptz,
    Varchar,
)
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.constraints import Check, Unique
from piccolo.table import Table

from config import (
    SEASON_CODE_MAX_LENGTH,
    SEASON_NAME_MAX_LENGTH,
    SEASON_TEAM_SIZE_MAX,
    SEASON_TEAM_SIZE_MIN,
    TEAM_CODE_MAX_LENGTH,
    TEAM_NAME_MAX_LENGTH,
)
from core.errors import (
    DuplicatePhase,
    DuplicateSeasonCode,
    DuplicateTeamCode,
    DuplicateTeamName,
    InvalidSeasonCode,
    InvalidSeasonName,
    InvalidSeasonTeamSize,
    InvalidTeamCode,
    InvalidTeamName,
    MissingGuildConfiguration,
    PhaseInMatch,
    PhaseNotFound,
    PlayerNotInTeam,
    SeasonNotActive,
    SeasonNotFound,
    TeamNotFound,
)
from data.enums import MatchStatus, PhaseName, SeasonStatus


def utc_now() -> datetime:
    return datetime.now(UTC)


class BaseTable(Table):
    id = Serial(primary_key=True)
    created_at = Timestamptz(default=TimestamptzNow())
    modified_at = Timestamptz(default=TimestamptzNow(), auto_update=utc_now)


class Guild(BaseTable):
    guild_id = BigInt(unique=True)
    host_role_id = BigInt(unique=True)
    participant_role_id = BigInt(unique=True)
    game_channel_id = BigInt(unique=True)
    results_channel_id = BigInt(unique=True)

    async def start_season(
        self, name: str, code: str, team_size: int, starts_at: datetime
    ) -> Season:
        season = Season(
            name=name,
            code=code,
            team_size=team_size,
            starts_at=starts_at,
            guild=self,
        )
        try:
            await season.save()
        except UniqueViolationError as error:
            if error.constraint_name == "unique_season_guild_code":
                raise DuplicateSeasonCode() from None
            raise error

        except CheckViolationError as error:
            match error.constraint_name:
                case "check_season_name_not_empty":
                    raise InvalidSeasonName() from None
                case "check_season_code_not_empty":
                    raise InvalidSeasonCode() from None
                case "check_season_team_size":
                    raise InvalidSeasonTeamSize() from None
                case _:
                    raise error

        except StringDataRightTruncationError as error:
            if len(name) > SEASON_NAME_MAX_LENGTH:
                raise InvalidSeasonName() from None
            if len(code) > SEASON_CODE_MAX_LENGTH:
                raise InvalidSeasonCode() from None

            raise error

        return season

    async def finish_season(self, season_code: str) -> Season:
        season = await self.get_season_by_code(season_code)

        season.status = SeasonStatus.FINISHED

        await season.save()

        return season

    async def get_seasons(self) -> list[Season]:
        return (
            await Season.objects()
            .where(Season.guild == self)
            .order_by(Season.starts_at, ascending=False)
        )

    async def get_active_seasons(self) -> list[Season]:
        return (
            await Season.objects()
            .where((Season.guild == self) & (Season.status == SeasonStatus.ACTIVE))
            .order_by(Season.starts_at, ascending=False)
        )

    async def get_season_by_code(self, season_code: str) -> Season:

        season = (
            await Season.objects()
            .where((Season.guild == self) & (Season.code == season_code))
            .first()
        )

        if season is None:
            raise SeasonNotFound()

        return season

    async def get_active_season_by_code(self, season_code: str) -> Season:

        season = await self.get_season_by_code(season_code)

        if season.status != SeasonStatus.ACTIVE:
            raise SeasonNotActive()

        return season


class Season(BaseTable):
    name = Varchar(length=SEASON_NAME_MAX_LENGTH)
    code = Varchar(length=SEASON_CODE_MAX_LENGTH)
    team_size = Integer()
    starts_at = Timestamptz(default=TimestamptzNow())
    status = Text(default=SeasonStatus.ACTIVE, choices=SeasonStatus)
    guild = ForeignKey(references=Guild, on_delete=OnDelete.cascade)

    unique_season_guild_code = Unique([guild, code], name="unique_season_guild_code")
    check_season_name_not_empty = Check(
        name != "",
        name="check_season_name_not_empty",
    )
    check_season_code_not_empty = Check(
        code != "",
        name="check_season_code_not_empty",
    )
    check_season_team_size = Check(
        (team_size >= SEASON_TEAM_SIZE_MIN) & (team_size <= SEASON_TEAM_SIZE_MAX),
        name="check_season_team_size",
    )

    def __str__(self) -> str:
        return f"{self.name} • {self.starts_at.strftime('%B %Y')}"

    async def schedule_phase(self, name: PhaseName) -> Phase:
        phase = Phase(name=name, season=self)

        try:
            await phase.save()
        except UniqueViolationError as error:
            if error.constraint_name == "unique_phase_season_name":
                raise DuplicatePhase() from None
            raise

        return phase

    async def get_phases(self) -> list[Phase]:
        return await Phase.objects().where(Phase.season == self).order_by(Phase.created_at)

    async def get_phase_by_name(self, name: PhaseName) -> Phase:
        phase = await Phase.objects().where((Phase.season == self) & (Phase.name == name)).first()

        if phase is None:
            raise PhaseNotFound()

        return phase

    async def delete_phase(self, name: PhaseName) -> Phase:
        phase = await self.get_phase_by_name(name)

        try:
            await phase.remove()
        except ForeignKeyViolationError:
            raise PhaseInMatch() from None

        return phase

    async def create_team(self, name: str, code: str) -> Team:
        team = Team(
            name=name,
            code=code,
            season=self,
        )

        try:
            await team.save()
        except UniqueViolationError as error:
            match error.constraint_name:
                case "unique_team_season_name":
                    raise DuplicateTeamName() from None
                case "unique_team_season_code":
                    raise DuplicateTeamCode() from None
                case _:
                    raise error
        except CheckViolationError as error:
            match error.constraint_name:
                case "check_team_name_not_empty":
                    raise InvalidTeamName() from None
                case "check_team_code_not_empty":
                    raise InvalidTeamCode() from None
                case _:
                    raise error
        except StringDataRightTruncationError as error:
            if len(name) > TEAM_NAME_MAX_LENGTH:
                raise InvalidTeamName() from None
            if len(code) > TEAM_CODE_MAX_LENGTH:
                raise InvalidTeamCode() from None
            raise error

        return team

    async def get_teams(self) -> list[Team]:
        return await Team.objects().where(Team.season == self).order_by(Team.name)

    async def get_team_by_code(self, team_code: str) -> Team:
        team = await Team.objects().where((Team.season == self) & (Team.code == team_code)).first()

        if team is None:
            raise TeamNotFound()

        return team

    async def has_player(self, user_id: int) -> bool:
        return await TeamMember.exists().where(
            (TeamMember.season == self) & (TeamMember.user_id == user_id)
        )

    async def schedule_match(
        self,
        phase: Phase,
        team_a: Team,
        team_b: Team,
        thread_id: int,
    ) -> Match:
        match = Match(
            season=self,
            phase=phase,
            team_a=team_a,
            team_b=team_b,
            thread_id=thread_id,
        )

        await match.save()

        return match


class Phase(BaseTable):
    name = Text(choices=PhaseName)
    season = ForeignKey(references=Season, on_delete=OnDelete.cascade)

    unique_phase_season_name = Unique([season, name], name="unique_phase_season_name")

    def __str__(self) -> str:
        return self.name


class Team(BaseTable):
    name = Varchar(length=TEAM_NAME_MAX_LENGTH)
    code = Varchar(length=TEAM_CODE_MAX_LENGTH)
    season = ForeignKey(references=Season)

    unique_team_season_name = Unique([season, name], name="unique_team_season_name")
    unique_team_season_code = Unique([season, code], name="unique_team_season_code")
    check_team_name_not_empty = Check(
        name != "",
        name="check_team_name_not_empty",
    )
    check_team_code_not_empty = Check(
        code != "",
        name="check_team_code_not_empty",
    )

    def __str__(self) -> str:
        return self.name

    async def get_members(self) -> list[TeamMember]:
        return (
            await TeamMember.objects().where(TeamMember.team == self).order_by(TeamMember.user_id)
        )

    async def add_member(self, user_id: int) -> TeamMember:
        member = TeamMember(
            user_id=user_id,
            season=self.season,
            team=self,
        )
        await member.save()

        return member

    async def remove_member(self, user_id: int) -> TeamMember:
        member = (
            await TeamMember.objects()
            .where((TeamMember.team == self) & (TeamMember.user_id == user_id))
            .first()
        )

        if member is None:
            raise PlayerNotInTeam()

        await member.remove()

        return member

    async def get_members_count(self) -> int:
        return await TeamMember.count().where(TeamMember.team == self)


class TeamMember(BaseTable):
    user_id = BigInt()
    season = ForeignKey(references=Season, on_delete=OnDelete.cascade)
    team = ForeignKey(references=Team, on_delete=OnDelete.cascade)

    unique_team_member_season_user = Unique(
        [season, user_id], name="unique_team_member_season_user"
    )
    unique_team_member_team_user = Unique([team, user_id], name="unique_team_member_team_user")


class Match(BaseTable):
    season = ForeignKey(references=Season, on_delete=OnDelete.cascade)
    phase = ForeignKey(references=Phase, on_delete=OnDelete.restrict)
    team_a = ForeignKey(references=Team, on_delete=OnDelete.restrict)
    team_b = ForeignKey(references=Team, on_delete=OnDelete.restrict)
    thread_id = BigInt(null=True)
    status = Text(default=MatchStatus.OPEN, choices=MatchStatus)


async def configure_guild(
    guild_id: int,
    host_role_id: int,
    participant_role_id: int,
    game_channel_id: int,
    results_channel_id: int,
):

    guild = await Guild.objects().where(Guild.guild_id == guild_id).first()

    if guild:
        guild.host_role_id = host_role_id
        guild.participant_role_id = participant_role_id
        guild.game_channel_id = game_channel_id
        guild.results_channel_id = results_channel_id
        await guild.save()

        created = False

    else:
        guild = Guild(
            guild_id=guild_id,
            host_role_id=host_role_id,
            participant_role_id=participant_role_id,
            game_channel_id=game_channel_id,
            results_channel_id=results_channel_id,
        )
        await guild.save()
        created = True

    return guild, created


async def get_guild(guild_id: int) -> Guild:
    guild = await Guild.objects().where(Guild.guild_id == guild_id).first()

    if not guild:
        raise MissingGuildConfiguration()

    return guild
