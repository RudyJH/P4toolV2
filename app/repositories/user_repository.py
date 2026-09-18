from passlib.context import CryptContext
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── CREATE ────────────────────────────────────────────────────────
    async def create(self, data: UserCreate) -> User:
        user = User(
            email=data.email,
            username=data.username,
            password_hash=pwd_context.hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    # ── READ ──────────────────────────────────────────────────────────
    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == str(user_id)))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_users(self, page=1, limit=20, role=None):
        query = select(User)
        count_q = select(func.count()).select_from(User)
        if role:
            query = query.where(User.role == role)
            count_q = count_q.where(User.role == role)
        offset = (page - 1) * limit
        query = query.order_by(User.created_at.desc()).offset(offset).limit(limit)
        rows = await self.db.execute(query)
        count_row = await self.db.execute(count_q)
        return list(rows.scalars().all()), count_row.scalar_one()

    # ── UPDATE ────────────────────────────────────────────────────────
    async def update(self, user_id: uuid.UUID, data: UserUpdate) -> User | None:
        changes = data.model_dump(exclude_none=True)
        if not changes:
            return await self.get_by_id(user_id)
        stmt = update(User).where(User.id == str(user_id)).values(**changes)
        await self.db.execute(stmt)
        return await self.get_by_id(user_id)

    # ── DELETE ────────────────────────────────────────────────────────
    async def delete(self, user_id: uuid.UUID) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        return True
