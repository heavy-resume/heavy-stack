from sqlmodel.ext.asyncio.session import AsyncSession

from heavy_stack.backend.data.repositories.user_repositories import UserRepository
from heavy_stack.backend.data.sql_models.users import SQLUser


class TestUserRepository:
    class TestCreateUser:
        async def test_creates_a_user_with_public_and_private_keys(self, db_session: AsyncSession) -> None:
            user = SQLUser()
            user.generate_public_private_keys()
            await UserRepository(db_session).create_user(user)
