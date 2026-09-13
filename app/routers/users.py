""" Application: PPPPdev
    File: app/routers/users.py 
    This file defines the API routes for managing users in the FastAPI application.
    It includes endpoints for listing users, retrieving a single user by ID, creating a new user, updating an existing user, and deleting a user.
    The routes use dependency injection to access the   UserRepository, which handles the database operations for users.
    The API follows RESTful conventions and returns appropriate HTTP status codes and responses for each operation.
    Requiments: FastAPI, SQLAlchemy 2, PostgreSQL   

"""


from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserCreate, UserListResponse, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])
DbDep = Annotated[AsyncSession, Depends(get_db)]

def get_repo(db: DbDep) -> UserRepository:
    return UserRepository(db)

RepoDep = Annotated[UserRepository, Depends(get_repo)]


@router.get("/", response_model=UserListResponse)
async def list_users(
    repo: RepoDep,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: str | None = Query(None),
):
    users, total = await repo.list_users(page=page, limit=limit, role=role)
    return UserListResponse(
        data=[UserResponse.model_validate(u) for u in users],
        total=total, page=page, limit=limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, repo: RepoDep):
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(body: UserCreate, repo: RepoDep):
    if await repo.get_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = await repo.create(body)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: uuid.UUID, body: UserUpdate, repo: RepoDep):
    user = await repo.update(user_id, body)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: uuid.UUID, repo: RepoDep):
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
