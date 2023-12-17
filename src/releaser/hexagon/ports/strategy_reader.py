"""This module defines the StrategyReader abstract base class."""

import abc

from ..entities import strategy


class StrategyReader(abc.ABC):
    """Abstract base class for reading strategy from current project."""

    @abc.abstractmethod
    def detect(self) -> strategy.ReleaseStrategy | None:
        """Detect strategy from current project."""
        raise NotImplementedError
