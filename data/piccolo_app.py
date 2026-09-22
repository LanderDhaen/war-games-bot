from pathlib import Path

from piccolo.conf.apps import AppConfig

from data.database import Guild, Match, Phase, Season, Team, TeamMember

APP_CONFIG = AppConfig(
    app_name="war_games",
    migrations_folder_path=Path(__file__).parent / "piccolo_migrations",
    table_classes=[Guild, Season, Phase, Team, TeamMember, Match],
    migration_dependencies=[],
    commands=[],
)
