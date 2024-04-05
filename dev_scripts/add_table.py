import textwrap
from pathlib import Path

project_base_path = "heavy_stack"

base_path = Path(__file__).parent.parent / project_base_path
data_path = base_path / "backend" / "data"


def main():
    while not (table_name := input("Enter table name: ").lower()):
        print("Table name is required")
    object_name_singular = table_name.rstrip("s")

    while not (model := input("Enter SQL model name: ")).startswith("SQL"):
        print("Model name must start with 'SQL'")
    model_no_sql = model[3:]
    print(f"Shared model will be named {model_no_sql}")

    while not (pk_type_name := input("Enter PK type name: ")).endswith("Id"):
        print("PK type name is required and must end in 'Id'")
    sql_model_path = data_path / "sql_models" / f"{table_name}.py"
    print(f"SQL model file path: {sql_model_path}")
    repository_file_basename = f"{table_name.rstrip('s')}_repository"
    repository_path = data_path / "repositories" / f"{repository_file_basename}.py"
    print(f"Repository file path: {repository_path}")
    repository_name = f"{model_no_sql}Repository"
    print(f"Repository will be named {repository_name}")
    manager_file_basename = f"{table_name.rstrip('s')}_managers"
    manager_path = data_path / "model_managers" / f"{manager_file_basename}.py"
    print(f"Manager file path: {manager_path}")
    manager_name = f"{model_no_sql}Manager"
    print(f"Manager will be named {manager_name}")
    munger_file_basename = f"{table_name.rstrip('s')}_model_mungers"
    model_munger_path = data_path / "model_mungers" / f"{munger_file_basename}.py"
    sql_munger_name = f"{model_no_sql}SQLModelMunger"
    non_sql_munger_name = f"{model_no_sql}ModelMunger"
    print(f"Munger file path: {model_munger_path}")
    print(f"Munger names will be {sql_munger_name} and {non_sql_munger_name}")

    shared_model_path = base_path / "shared_models" / f"{table_name}.py"
    print(f"Shared model file path: {shared_model_path}")
    if sql_model_path.exists():
        print(f"{sql_model_path} already exists")
        return
    if repository_path.exists():
        print(f"{repository_path} already exists")
        return
    if manager_path.exists():
        print(f"{manager_path} already exists")
        return
    if shared_model_path.exists():
        print(f"{shared_model_path} already exists")
        return

    with shared_model_path.open("w") as f:
        f.write(
            textwrap.dedent(
                f"""
                from pydantic import BaseModel

                {pk_type_name} = str

                class {model_no_sql}(BaseModel):
                    id: {pk_type_name}
                """
            ).lstrip()
        )

    with sql_model_path.open("w") as f:
        f.write(
            textwrap.dedent(
                f"""
                from uuid import uuid4

                from sqlmodel import SQLModel, Field

                from {project_base_path}.shared_models.{table_name} import {pk_type_name}


                class {model}(SQLModel, table=True):
                    __tablename__ = "{table_name}"

                    id: {pk_type_name} = Field(default_factory=lambda: uuid4().hex, primary_key=True)
                """
            ).lstrip()
        )

    with repository_path.open("w") as f:
        f.write(
            textwrap.dedent(
                f"""
                from {project_base_path}.backend.data.repositories.base_repositories import SQLRepositoryBase
                from {project_base_path}.backend.data.sql_models.{table_name} import {model}
                from {project_base_path}.shared_models.{table_name} import {pk_type_name}


                class {repository_name}(SQLRepositoryBase):
                    async def create_{object_name_singular}(
                        self, {object_name_singular}: {model}
                    ) -> {model}:
                        self._db_session.add({object_name_singular})
                        return {object_name_singular}

                    async def get_{object_name_singular}(
                        self, {object_name_singular}_id: {pk_type_name}
                    ) -> {model} | None:
                        return await self._db_session.get({model}, {object_name_singular}_id)
                """
            ).lstrip()
        )

    with manager_path.open("w") as f:
        f.write(
            textwrap.dedent(
                f"""
                from functools import cached_property
                from typing import TypeVar
                from {project_base_path}.backend.data.model_managers.base_managers import BaseManager

                from {project_base_path}.backend.data.model_mungers.{munger_file_basename} import ModelMunger, {sql_munger_name}, {non_sql_munger_name}
                from {project_base_path}.backend.data.repositories.{repository_file_basename} import {repository_name}
                from {project_base_path}.backend.data.sql_models.{table_name} import {model}
                from {project_base_path}.shared_models.{table_name} import {model_no_sql}, {pk_type_name}

                T = TypeVar("T", bound={model_no_sql} | {model})

                class {manager_name}(BaseManager):
                    possible_mungers = ({non_sql_munger_name}, {sql_munger_name})

                    def __init__(
                        self,
                        model_munger: ModelMunger[T, {model}],
                    ) -> None:
                        self._model_munger = model_munger

                        super().__init__(model_munger)

                    @cached_property
                    def _{table_name}_repository(self) -> {repository_name}:
                        return {repository_name}()

                    async def get_{object_name_singular}_by_id(
                        self, {object_name_singular}_id: {pk_type_name}
                    ) -> T | None:
                        result = await self._{table_name}_repository.get_{object_name_singular}({object_name_singular}_id)
                        return self._model_munger.to_model(result)
                """
            ).lstrip()
        )

    with model_munger_path.open("w") as f:
        f.write(
            textwrap.dedent(
                f"""
                from {project_base_path}.backend.data.model_mungers.base_mungers import ModelMunger, SQLModelMunger
                from {project_base_path}.backend.data.sql_models.{table_name} import {model}
                from {project_base_path}.shared_models.{table_name} import {model_no_sql}


                class {sql_munger_name}(SQLModelMunger[{model}]):
                    sql_model = {model}
                    target_model = {model}


                class {non_sql_munger_name}(ModelMunger[{model_no_sql}, {model}]):
                    sql_model = {model}
                    target_model = {model_no_sql}

                    def to_model(self, sql_model: {model} | None) -> {model_no_sql} | None:
                        if sql_model is None:
                            return None
                        return {model_no_sql}(id=sql_model.id)
                """
            ).lstrip()
        )


if __name__ == "__main__":
    main()
