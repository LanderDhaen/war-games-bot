from datetime import UTC, datetime

from piccolo.columns import (
    BigInt,
    Serial,
    Timestamptz,
)
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.table import Table


def utc_now() -> datetime:
    return datetime.now(UTC)


class BaseMixin:
    id = Serial(primary_key=True)
    created_at = Timestamptz(default=TimestamptzNow())
    modified_at = Timestamptz(default=TimestamptzNow(), auto_update=utc_now)


class Guild(BaseMixin, Table):
    guild_id = BigInt(unique=True)
    host_role_id = BigInt()
    participant_role_id = BigInt()
    game_channel_id = BigInt()
    results_channel_id = BigInt()
