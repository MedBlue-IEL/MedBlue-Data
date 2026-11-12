from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import alembic_postgresql_enum

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to sys.path

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
from sqlmodel import SQLModel
from src.models.projects import Project
from src.models.campaign_events import CampaignEvent
from src.models.habitats import Habitat
from src.models.municipalities import Municipality
from src.models.stations import Station
from src.models.station_geometries import StationGeometry
from src.models.sampling_events import SamplingEvent
from src.models.carlit import Carlit
from src.models.species import Species
from src.models.occurrences import Occurrence

target_metadata = SQLModel.metadata

# Locate the .env file in the parent folder
env_path = Path(__file__).resolve().parent.parent / ".env"
# Explicitly load the .env file into environment variables
# override=True ensures it replaces existing keys if needed
load_dotenv(dotenv_path=env_path, override=True)

# 💡 Use environment variables so you don't hardcode sensitive credentials!
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/medblue"
)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


naming_convention = {
    "ix": "ix_%(table_name)s_%(column_0_label)s",  # Added table_name for more uniqueness
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # Used constraint_name for check constraints
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = DATABASE_URL
    # url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        naming_convention=naming_convention,  # Add naming convention
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use DATABASE_URL (not the fixed URL of alembic.ini) so it works inside Docker
    ini_section = config.get_section(config.config_ini_section, {})
    ini_section["sqlalchemy.url"] = DATABASE_URL
    connectable = engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            compare_type=True,  # Detects column type changes
            naming_convention=naming_convention,  # Add naming convention
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
