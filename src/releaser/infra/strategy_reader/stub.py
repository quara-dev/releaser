from __future__ import annotations

from releaser.hexagon.entities import strategy
from releaser.hexagon.ports import StrategyReader


class StrategyReaderStub(StrategyReader):
    """A stub strategy reader that can be used for testing."""

    def __init__(self) -> None:
        self.strategy: strategy.ReleaseStrategy | None = None

    def read(self) -> strategy.ReleaseStrategy | None:
        return self.strategy

    def set_strategy(self, strategy: strategy.ReleaseStrategy) -> None:
        """Test helper: set the strategy to be returned by read()."""
        self.strategy = strategy
