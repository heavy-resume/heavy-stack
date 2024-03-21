from reactpy.core.types import ContextProviderType
from reactpy.types import Component as ReactpyComponent
from reactpy.types import VdomDict

Component = VdomDict | ReactpyComponent | ContextProviderType | str
