from sqlmodel import SQLModel
from sqlmodel.main import SQLModelMetaclass


class HeavyModelMeta(SQLModelMetaclass):
    def __new__(mcs, name, bases, dct, **kwargs):
        if name != "HeavyModel":
            if not kwargs.get("table", False):
                raise TypeError(f"The 'table' argument must be set to True in {name}. Kwargs: {kwargs}")
            if not dct.get("__tablename__"):
                raise TypeError(f"The '__tablename__' attribute must be set in {name}.")
        return super().__new__(mcs, name, bases, dct, **kwargs)


class HeavyModel(SQLModel, metaclass=HeavyModelMeta):
    """
    Use this instead of SQLModel so that QoL checks are performed.
    """
