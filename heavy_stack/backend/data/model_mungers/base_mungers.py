from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar, cast

from sqlmodel import SQLModel

T = TypeVar("T")
G = TypeVar("G", bound=SQLModel)


class ModelMunger(Generic[T, G], metaclass=ABCMeta):
    sql_model: type[G]
    target_model: type[T]

    @abstractmethod
    def to_model(self, sql_model: G | None) -> T | None:
        """
        Return the conversion from a SQL Model to the target model

        :param sql_model: Incoming sql model
        :return: The target model
        """


class SQLModelMunger(ModelMunger[G, G], Generic[G], metaclass=ABCMeta):
    def to_model(self, sql_model: G | None) -> T | None:
        return cast(T, sql_model)
