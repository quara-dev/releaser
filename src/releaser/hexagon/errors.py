"""Custom errors for releaser hexagon."""
from __future__ import annotations


class ReleaseStrategyNotFoundError(Exception):
    def __init__(self):
        super().__init__("Cannot find any release strategy in current directory")
