import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from database import get_session
from models.projects import Project
from src.main import app
from sqlalchemy.pool import StaticPool


PROJECT = {
    "project_code": "TEST_PROJECT",
    "project_name": "Test Project"
}


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_projects(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)

    response = client.post("/projects/", json=PROJECT).content.decode("utf-8")
    assert json.loads(response).get("id") is not None

def test_get_projects(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)

    db_project = Project.model_validate(PROJECT)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)

    response = client.get("/projects/").content.decode("utf-8")
    assert len(json.loads(response)) > 0
    assert json.loads(response)[0].get("id") is not None

def test_get_project_by_code(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)

    db_project = Project.model_validate(PROJECT)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)

    dirty_project_code = " _tEst pRojéct *"
    response = client.get("/projects/code/" + dirty_project_code).content.decode("utf-8")
    assert json.loads(response).get("project_code") == PROJECT.get("project_code")