# MedBlue-Data

Backend server for the MedBlue project.

## Setup

Local execution
```shell
 uv run uvicorn main:app --reload --app-dir src
```
Swagger Documentation: http://localhost:8000/docs

## Test

```shell
uv run pytest --tb=short
```
## Alembic

Keep the database in sync with the code

```shell
 alembic check 
 alembic revision --autogenerate -m "Add new table"
alembic upgrade head
```