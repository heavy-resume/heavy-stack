from functools import cached_property
from typing import Generic, TypeVar

from heavy_stack.backend.data.model_managers.base_managers import BaseManager
from heavy_stack.backend.data.model_mungers.base_mungers import ModelMunger
from heavy_stack.backend.data.model_mungers.user_model_mungers import UserModelMunger, UserSQLModelMunger
from heavy_stack.backend.data.repositories.user_repositories import UserRepository
from heavy_stack.backend.data.sql_models.users import (
    SQLUser,
    UserPublicKeyEncryptedPayload,
)
from heavy_stack.shared_models.users import User, UserId

T = TypeVar("T", bound=User | SQLUser)


class UserManager(BaseManager, Generic[T]):
    possible_mungers = (UserModelMunger, UserSQLModelMunger)

    def __init__(
        self,
        model_munger: ModelMunger[T, SQLUser],
    ) -> None:
        self._model_munger: ModelMunger[T, SQLUser] = model_munger

        super().__init__(model_munger)

    @cached_property
    def _user_repository(self) -> UserRepository:
        return UserRepository()

    async def get_user(self, user_id: UserId) -> T | None:
        return self._model_munger.to_model(await self._user_repository.get_user(user_id))

    async def encrypt_using_public_key(
        self,
        data: bytes,
        user_id_to_encrypt_for: UserId,
    ) -> UserPublicKeyEncryptedPayload:
        user = await self._user_repository.get_user(user_id_to_encrypt_for)
        assert user is not None
        return user.encrypt_with_public_key(data)
