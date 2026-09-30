from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models.projects import Project

router = APIRouter(prefix="/projects", tags=["Projects"])


# 1. CREATE a new project
@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project: Project, session: Session = Depends(get_session)) -> Project:
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


# 2. READ all projects (with simple pagination limits)
@router.get("/", response_model=list[Project])
def read_projects(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Project).offset(offset).limit(limit)
    projects = session.exec(statement).all()
    return projects


# 3. READ a single project by ID
@router.get("/{project_id}", response_model=Project)
def read_project(project_id: int, session: Session = Depends(get_session)) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# 4. UPDATE an existing project
@router.put("/{project_id}", response_model=Project)
def update_project(project_id: int, updated_data: Project, session: Session = Depends(get_session)) -> Project:
    db_project = session.get(Project, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Exclude fields like 'id' or 'created_at' from rewriting
    data_to_update = updated_data.model_dump(exclude_unset=True, exclude={"id", "created_at"})
    for key, value in data_to_update.items():
        setattr(db_project, key, value)

    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project


# 5. DELETE a project
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, session: Session = Depends(get_session)) -> None:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    session.delete(project)
    session.commit()
