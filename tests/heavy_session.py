from sqlmodel.ext.asyncio.session import AsyncSession

from heavy_stack.backend.data.sql_models.heavy_models import HeavyModel


class HeavySession(AsyncSession):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.objects: dict[str, HeavyModel] = {}

    def add(self, obj):
        self.objects[getattr(obj, "id", str(obj))] = obj
        return super().add(obj)

    def __getattr__(self, attr):
        return getattr(self.session, attr)
