from pathlib import Path

from piccolo.conf.apps import AppConfig

from data.database import Guild

APP_CONFIG = AppConfig(
    app_name="wg",
    migrations_folder_path="data/migrations",
    table_classes=[Guild],
    migration_dependencies=[],
    commands=[],
)
