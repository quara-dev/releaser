from __future__ import annotations

import abc

from ..entities import bakery


class ImageBaker(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def bake(self, spec: bakery.ImagesSpec) -> None:
        """Bake a spec."""
