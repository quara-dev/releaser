from __future__ import annotations

from releaser.hexagon.entities import bakery
from releaser.hexagon.ports import ImageBaker


class ImageBakerStub(ImageBaker):
    def __init__(self) -> None:
        self.spec: bakery.ImagesSpec | None = None
        self._bake_calls: list[bakery.ImagesSpec] = []

    def bake(self, spec: bakery.ImagesSpec) -> None:
        self._bake_calls.append(spec)
        self.spec = spec

    def did_bake(self, spec: bakery.ImagesSpec) -> bool:
        """Test helper: check if the spec was baked."""
        return spec in self._bake_calls

    def get_bake_calls(self) -> list[bakery.ImagesSpec]:
        """Test helper: get the bake calls."""
        return self._bake_calls

    def reset(self) -> None:
        """Test helper: reset the stub."""
        self._bake_calls = []
