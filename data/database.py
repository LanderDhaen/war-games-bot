from datetime import UTC, datetime

from piccolo.columns import (
    BigInt,
    ForeignKey,
    OnDelete,
    Serial,
    Timestamptz,
    Varchar,
)
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.constraints import Unique
from piccolo.table import Table


def utc_now() -> datetime:
    return datetime.now(UTC)


class IdentityMixin:
    id = Serial(primary_key=True)


class MetaMixin:
    created_at = Timestamptz(default=TimestamptzNow())
    modified_at = Timestamptz(default=TimestamptzNow(), auto_update=utc_now)


class Guild(MetaMixin, Table):
    guild_id = BigInt(primary_key=True)
    joined_at = Timestamptz(default=TimestamptzNow())
    left_at = Timestamptz(null=True, default=None)


class Configuration(IdentityMixin, MetaMixin, Table):
    host_role_id = BigInt()
    participant_role_id = BigInt()
    game_channel_id = BigInt()
    results_channel_id = BigInt()
    guild = ForeignKey(
        references=Guild,
        null=False,
        on_delete=OnDelete.restrict,
        unique=True,
    )


class Tournament(IdentityMixin, MetaMixin, Table):
    name = Varchar(length=90)
    guild = ForeignKey(references=Guild, null=False, on_delete=OnDelete.restrict)

    unique_tournament_name_guild = Unique([name, guild], name="unique_tournament_name_guild")
