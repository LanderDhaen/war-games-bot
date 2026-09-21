from discord import app_commands

from config import (
    SEASON_CODE_MAX_LENGTH,
    SEASON_CODE_MIN_LENGTH,
    SEASON_NAME_MAX_LENGTH,
    SEASON_NAME_MIN_LENGTH,
    SEASON_TEAM_SIZE_MAX,
    SEASON_TEAM_SIZE_MIN,
    TEAM_NAME_MAX_LENGTH,
    TEAM_NAME_MIN_LENGTH,
)

class UserFacingError(app_commands.AppCommandError):
    title: str
    message: str

    def __init__(self, message: str | None = None):
        if message is not None:
            self.message = message

        super().__init__(self.message)

class MissingGuildConfiguration(UserFacingError, app_commands.CheckFailure):
    title = "Missing Configuration"
    message = "This server is not yet configured. An administrator can use `/setup server` to get started."

class MissingHostRole(UserFacingError, app_commands.CheckFailure):
    title = "Missing Permission"
    message = "You need to be a host to use this command."

class MissingAdministratorPermission(UserFacingError, app_commands.CheckFailure):
    title = "Missing Permission"
    message = "You need to be an administrator to use this command."

class GuildOnly(UserFacingError, app_commands.CheckFailure):
    title = "Missing Permission"
    message = "This command can only be used in a server."

class MissingHostRoleConfiguration(UserFacingError):
    title = "Missing Configuration"
    message = "The configured host role no longer exists. Use `/setup server` to reconfigure the settings."

class MissingParticipantRoleConfiguration(UserFacingError):
    title = "Missing Configuration"
    message = "The configured participant role no longer exists. Use `/setup server` to reconfigure the settings."

class MissingGameChannelConfiguration(UserFacingError):
    title = "Missing Configuration"
    message = "The configured game channel no longer exists. Use `/setup server` to reconfigure the settings."

class MissingResultsChannelConfiguration(UserFacingError):
    title = "Missing Configuration"
    message = "The configured results channel no longer exists. Use `/setup server` to reconfigure the settings."

class InvalidSeasonName(UserFacingError):
    title = "Invalid Configuration"
    message = f"The season name must contain between {SEASON_NAME_MIN_LENGTH} and {SEASON_NAME_MAX_LENGTH} characters."

class InvalidSeasonCode(UserFacingError):
    title = "Invalid Configuration"
    message = f"The season code must contain between {SEASON_CODE_MIN_LENGTH} and {SEASON_CODE_MAX_LENGTH} characters."

class DuplicateSeasonCode(UserFacingError):
    title = "Invalid Configuration"
    message = "A season with this code already exists in this server."

class InvalidSeasonTeamSize(UserFacingError):
    title = "Invalid Configuration"
    message = f"The team size must be between {SEASON_TEAM_SIZE_MIN} and {SEASON_TEAM_SIZE_MAX} players."

class InvalidSeasonStart(UserFacingError):
    title = "Invalid Configuration"
    message = "This is not a valid date and time. Please use the ISO format, for example `2026-09-20 19:00`."

class SeasonNotFound(UserFacingError):
    title = "Invalid Configuration"
    message = "There's no season with this ID."

class SeasonNotActive(UserFacingError):
    title = "Invalid Configuration"
    message = "This season is not active."

class InvalidTeamName(UserFacingError):
    title = "Invalid Configuration"
    message = f"The team name must contain between {TEAM_NAME_MIN_LENGTH} and {TEAM_NAME_MAX_LENGTH} characters."

class DuplicateTeamName(UserFacingError):
    title = "Invalid Configuration"
    message = "A team with this name already exists in this season."

class TeamNotFound(UserFacingError):
    title = "Invalid Configuration"
    message = "There's no team with this ID in this season."

class TeamsMustBeDifferent(UserFacingError):
    title = "Invalid Configuration"
    message = "A team cannot play against itself."

class EmptyMatchTeam(UserFacingError):
    title = "Invalid Configuration"
    message = "Both teams need at least one player before scheduling a match."

class InvalidMatchConfiguration(UserFacingError):
    title = "Invalid Configuration"
    message = "The match could not be scheduled because the selected season or teams are no longer valid."

class MatchThreadCreationFailed(UserFacingError):
    title = "Something went wrong"
    message = "The private match thread could not be created."

class TeamInMatch(UserFacingError):
    title = "Invalid Configuration"
    message = "This team cannot be deleted because it is referenced by a match."

class BotTeamMember(UserFacingError):
    title = "Invalid Configuration"
    message = "Bots cannot be added to a team."

class MemberMissingParticipantRole(UserFacingError):
    title = "Invalid Configuration"
    message = "This player needs the participant role before joining a team."

class PlayerAlreadyAssigned(UserFacingError):
    title = "Invalid Configuration"
    message = "This player already belongs to a team in this season."

class PlayerNotInTeam(UserFacingError):
    title = "Invalid Configuration"
    message = "This player does not belong to this team."

class TeamFull(UserFacingError):
    title = "Invalid Configuration"
    message = "This team is already full."

class PlayerAddFailed(UserFacingError):
    title = "Invalid Configuration"
    message = "The player could not be added to this team."

class UnexpectedCommandError(UserFacingError):
    title = "Something went wrong"
    message = "Could not execute this command. Please try again."
