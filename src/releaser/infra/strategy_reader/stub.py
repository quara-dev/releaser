from __future__ import annotations

from releaser.hexagon.entities import strategy
from releaser.hexagon.ports import StrategyReader


class StrategyReaderStub(StrategyReader):
    def __init__(self) -> None:
        self.strategy: strategy.ReleaseStrategy | None = None

    def detect(self) -> strategy.ReleaseStrategy | None:
        return self.strategy

    def set_strategy(self, strategy: strategy.ReleaseStrategy) -> None:
        self.strategy = strategy
