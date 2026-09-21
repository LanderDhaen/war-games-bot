# Commands

Use these commands inside your Discord server. When a command asks for a season
or team, start typing its name or code and select it from the autocomplete list.

## Setup

Configure your server for War Games. Choose the roles and channels the bot
should use.

### `/setup server`

Configure your server for War Games. You can run this command again whenever
you want to update the configuration.

**Who can use it:** Server administrators

| Parameter          | Type         | Description                                                      |
| ------------------ | ------------ | ---------------------------------------------------------------- |
| `host-role`        | Role         | Role whose members can manage seasons, teams, and matches.       |
| `participant-role` | Role         | Role required before a member can be added to a team.            |
| `game-channel`     | Text channel | Channel where games will be posted.                              |
| `results-channel`  | Text channel | Parent channel used for match results and private match threads. |

## Season

Manage seasons for War Games. Schedule seasons, view their details, and mark
them as finished.

### `/season schedule`

Schedule a new season of War Games. Choose a short, memorable code because it
will be used to select the season in other commands.

**Who can use it:** Hosts

| Parameter   | Type    | Requirements                          | Description                                          |
| ----------- | ------- | ------------------------------------- | ---------------------------------------------------- |
| `name`      | String  | 1–100 characters                      | Name shown to members.                               |
| `code`      | String  | 1–10 characters; unique in the server | Short code used to select the season later.          |
| `team-size` | Integer | 1–5                                   | Maximum number of players on each team.              |
| `starts-at` | String  | ISO date and time                     | Start date and time, for example `2026-09-20 19:00`. |

### `/season info`

Display information about a season of War Games, including its name, format,
status, and number of teams.

| Parameter | Type        | Description                                                                                   |
| --------- | ----------- | --------------------------------------------------------------------------------------------- |
| `season`  | Season | Season to display. Active and finished seasons are available. |

### `/season finish`

Finish an active season of War Games.

**Who can use it:** Hosts

| Parameter | Type        | Description              |
| --------- | ----------- | ------------------------ |
| `season`  | Season | Active season to finish. |

## Team

Manage teams for War Games. Create teams, manage their players, and view team
information.

### `/team create`

Create a new team for a season of War Games. Choose a short code so the team is
easy to find in other commands.

**Who can use it:** Hosts

| Parameter | Type        | Requirements                           | Description                                   |
| --------- | ----------- | -------------------------------------- | --------------------------------------------- |
| `season`  | Season | Must be active | Season the team will participate in. |
| `name`    | String | 1–100 characters; unique in the season | Name shown to members. |
| `code`    | String | 1–10 characters; unique in the season | Short code used to select the team later. |

### `/team info`

Display information about a team, including its name, code, size, and players.

| Parameter | Type        | Description                                                     |
| --------- | ----------- | --------------------------------------------------------------- |
| `season`  | Season | Active season containing the team. |
| `team`    | Team | Team to display. Only teams from the selected season are shown. |

### `/team delete`

Delete a team from a season of War Games.

**Who can use it:** Hosts

| Parameter | Type        | Description                                                    |
| --------- | ----------- | -------------------------------------------------------------- |
| `season`  | Season | Active season containing the team. |
| `team`    | Team | Team to delete. Only teams from the selected season are shown. |

A team which is already part of a match cannot be deleted.

### `/team add-player`

Add a server member to a team.

**Who can use it:** Hosts

| Parameter | Type           | Description                                      |
| --------- | -------------- | ------------------------------------------------ |
| `season`  | Season | Active season containing the team. |
| `team`    | Team | Team the player should join. |
| `member`  | Member | Server member to add. |

The selected member must:

- be a real user, not a bot;
- have the configured participant role;
- not already belong to another team in the season; and
- fit within the team's player limit.

### `/team remove-player`

Remove a player from a team.

**Who can use it:** Hosts

| Parameter | Type           | Description                                            |
| --------- | -------------- | ------------------------------------------------------ |
| `season`  | Season | Active season containing the team. |
| `team`    | Team | Team to remove the player from. |
| `member`  | Member | Player who currently belongs to the selected team. |

## Match

Manage matches for War Games. Schedule matches and create a private place for
both teams to coordinate.

### `/match schedule`

Schedule a match between two teams. The bot creates a private thread in the
configured results channel and mentions the players from both teams.

**Who can use it:** Hosts

| Parameter | Type        | Description                                                                    |
| --------- | ----------- | ------------------------------------------------------------------------------ |
| `season`  | Season | Active season where the match will be played. |
| `team-a`  | Team | First participating team. |
| `team-b`  | Team | Second participating team. Team A is excluded from the choices. |

Both teams must belong to the selected season, must be different, and must each
have at least one player.
