from pathlib import Path
from typing import Any, Generator
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session
from sqlmodel import Session, create_engine, text
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.core import utils
from testcontainers.community.postgres import PostgresContainer

POSTGRES_IMAGE = "postgres:15-alpine"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "test_password"
POSTGRES_DATABASE = "test_database"
POSTGRES_CONTAINER_PORT = 5432

# Point Testcontainers & Ryuk to Docker Desktop's actual socket on macOS
docker_sock = Path.home() / ".docker" / "run" / "docker.sock"
if docker_sock.exists():
    os.environ.setdefault("DOCKER_HOST", f"unix://{docker_sock}")
    os.environ.setdefault("RYUK_HOST", f"unix://{docker_sock}")


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, Any, None]:
    """
    Setup postgres container
    """
    with PostgresContainer(
            image=POSTGRES_IMAGE,
            username=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            dbname=POSTGRES_DATABASE,
            port=POSTGRES_CONTAINER_PORT,
    ) as postgres:
        os.environ["DATABASE_URL"] = postgres.get_connection_url()
        yield postgres


@pytest.fixture(scope="session")
def db(postgres_container: PostgresContainer):
    from database import create_db_and_tables
    if utils.is_windows():
        postgres_container.get_container_host_ip = lambda: "localhost"
    url = postgres_container.get_connection_url()
    engine = create_engine(url, echo=False, future=True)
    create_db_and_tables()
    # initialize_test_db(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session")
def test_client(db):
    assert isinstance(db, Session)

    def override_get_session():
        yield db

    from database import get_session
    from main import app

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="module", autouse=True)
def verify_live_testcontainer_connection(postgres_container):
    import database

    expected_url = postgres_container.get_connection_url()
    actual_url = database.engine.url.render_as_string(hide_password=False)

    assert actual_url == expected_url, (
        f"SAFETY CHECK FAILED: Test is using {actual_url} instead of Testcontainer {expected_url}"
    )
    assert database.engine.url.port != 5432, "SAFETY CHECK FAILED: Connected to default port 5432!"

    expected_host_port = int(postgres_container.get_exposed_port(5432))

    # 1. Verify the SQLAlchemy engine points to the container's mapped host port
    assert database.engine.url.port == expected_host_port, (
        f"Engine port {database.engine.url.port} != container port {expected_host_port}"
    )

    # 2. Run a live query to confirm the session actually reaches PostgreSQL
    with Session(database.engine) as session:
        result = session.exec(text("SELECT 1")).scalar_one()
        assert result == 1

    print("Testcontainer connection verified successfully! Test database: " + postgres_container.get_connection_url())
