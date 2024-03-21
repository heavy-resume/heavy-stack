from abc import ABCMeta, abstractproperty
from typing import Container, Sequence

from heavy_stack.backend.data.model_mungers.base_mungers import ModelMunger


class BaseManager(metaclass=ABCMeta):
    def __init__(
        self,
        *model_mungers: ModelMunger,
    ) -> None:
        if __debug__:
            possible_mungers = self.possible_mungers

            def check_correct_type(model_munger, munger_group):
                assert (
                    type(model_munger) in munger_group
                ), f"Unexpected munger: {type(model_munger)} not in {munger_group}"

            for idx, model_munger in enumerate(model_mungers):
                if len(model_mungers) > 1:
                    munger_group = possible_mungers[idx]  # type: ignore
                else:
                    munger_group = possible_mungers
                check_correct_type(model_munger, munger_group)

    @abstractproperty
    def possible_mungers(
        self,
    ) -> Container[type[ModelMunger]] | Sequence[Container[type[ModelMunger]]]: ...
