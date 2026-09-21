from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

from config import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from the configuration.")

DB = PostgresEngine(config={"dsn": DATABASE_URL})

APP_REGISTRY = AppRegistry(apps=["data.piccolo_app"])
