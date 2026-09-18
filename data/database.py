from piccolo.table import Table
from piccolo.columns import OnDelete, Serial, ForeignKey, Text, Integer, Timestamptz, Varchar
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.constraints import Check, Unique

from data.enums import SeasonStatus, MatchStatus

class BaseTable(Table):
    id = Serial(primary_key=True)
    created_at = Timestamptz(default=TimestamptzNow())
    modified_at = Timestamptz(default=TimestamptzNow(), auto_update=TimestamptzNow())

class Guild(BaseTable):
    guild_id = Integer(unique=True)
    host_role_id = Integer(unique=True)
    participant_role_id = Integer(unique=True)
    results_channel_id = Integer(unique=True)

class Season(BaseTable):
    name = Varchar(length=100)
    team_size = Integer()
    starts_at = Timestamptz(default=TimestamptzNow())
    status = Text(default=SeasonStatus.ACTIVE, choices=SeasonStatus)
    guild = ForeignKey(references=Guild, on_delete=OnDelete.cascade)

    unique_name_guild = Unique([name, guild])
    check_team_size = Check((team_size > 0) & (team_size <= 5))

class Team(BaseTable):
    name = Varchar(length=100)
    season = ForeignKey(references=Season, on_delete=OnDelete.cascade)

    unique_name_season = Unique([name, season])

class TeamMember(BaseTable):
    user_id = Integer()
    season = ForeignKey(references=Season, on_delete=OnDelete.cascade)
    team = ForeignKey(references=Team, on_delete=OnDelete.cascade)

    unique_user_team_season = Unique([user_id, team, season])

class Match(BaseTable):
    season = ForeignKey(references=Season, on_delete=OnDelete.cascade)
    team_a = ForeignKey(references=Team, on_delete=OnDelete.restrict)
    team_b = ForeignKey(references=Team, on_delete=OnDelete.restrict)
    thread_id = Integer(null=True)
    status = Text(default=MatchStatus.OPEN, choices=MatchStatus)

