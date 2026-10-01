from collections.abc import Generator
import os
from sqlmodel import Session, SQLModel, create_engine
from pathlib import Path
from dotenv import load_dotenv

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

DATABASE_RECREATE = os.getenv(
    "DATABASE_RECREATE",
    "false"
)

# Connects smoothly to PostgreSQL via the psycopg binary driver
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables() -> None:

    # Drop al tables if configured
    if DATABASE_RECREATE == "true":
        # 1. Force drop everything (handling foreign key constraints via CASCADE)
        print("WARNING: Dropping all tables.")
        with engine.begin() as connection:
            # SQLModel / SQLAlchemy drop_all does not always handle PostgreSQL cascade perfectly
            # We explicitly bind a cascade drop or rely on metadata
            SQLModel.metadata.drop_all(connection)
        # 2. Clear out the connection pool to ensure no stale connections linger
        engine.dispose()

    # Create tables
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
