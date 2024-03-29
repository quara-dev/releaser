"""This module defines the StrategyReader abstract base class."""

from __future__ import annotations

import abc

from ..entities import strategy


class StrategyReader(abc.ABC):
    """Abstract base class for reading strategy from current project."""

    @abc.abstractmethod
    def read(self) -> strategy.ReleaseStrategy | None:
        """Detect strategy from current project."""
        raise NotImplementedError
