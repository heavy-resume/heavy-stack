from __future__ import annotations

from heavy_stack.backend.data.model_mungers.base_mungers import ModelMunger, SQLModelMunger
from heavy_stack.backend.data.sql_models.users import SQLUser
from heavy_stack.shared_models.users import User


class UserSQLModelMunger(SQLModelMunger[SQLUser]):
    sql_model = SQLUser
    target_model = SQLUser


class UserModelMunger(ModelMunger[User, SQLUser]):
    sql_model = SQLUser
    target_model = User

    def to_model(self, sql_model: SQLUser | None) -> User | None:
        if sql_model is None:
            return None
        return User(
            id=sql_model.id,
        )
