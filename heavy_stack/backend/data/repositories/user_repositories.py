from sqlmodel import select

from heavy_stack.backend.data.repositories.base_repositories import SQLRepositoryBase
from heavy_stack.backend.data.sql_models.users import SQLUser
from heavy_stack.shared_models.users import UserId


class UserRepository(SQLRepositoryBase):
    async def get_user(self, user_id: UserId) -> SQLUser | None:
        return await self._retrieve_user(SQLUser.id == user_id)

    async def _retrieve_user(self, *conditions) -> SQLUser | None:
        result = await self._db_session.exec(
            select(SQLUser).where(*conditions).limit(1),
        )
        return result.one_or_none()

    async def create_user(self, user: SQLUser) -> SQLUser:
        self._db_session.add(user)
        return user

    async def update_user(self, user: SQLUser) -> SQLUser:
        self._db_session.add(user)
        return user
