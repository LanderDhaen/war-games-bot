from piccolo.engine.sqlite import SQLiteEngine

DB = SQLiteEngine(
    path="db/war-games.db",
    timeout=60,
)
