from piccolo.conf.apps import AppConfig

from data.database import Configuration, Guild, Tournament

APP_CONFIG = AppConfig(
    app_name="wg",
    migrations_folder_path="data/migrations",
    table_classes=[Guild, Configuration, Tournament],
    migration_dependencies=[],
    commands=[],
)
