from collections.abc import Generator
import os
from sqlmodel import Session, SQLModel, create_engine

# 💡 Use environment variables so you don't hardcode sensitive credentials!
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/medblue"
)

# Connects smoothly to PostgreSQL via the psycopg binary driver
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
