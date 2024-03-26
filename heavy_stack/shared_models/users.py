from pydantic import BaseModel

UserId = str


class User(BaseModel):
    id: str


AnonymousUser = User(id="")
