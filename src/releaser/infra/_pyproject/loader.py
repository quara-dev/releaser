from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


class PyprojectLoader:
    """A base class to help working with pyproject.toml files."""

    def load_pyproject(self, filepath: Path) -> dict[str, Any]:
        """Load a pyproject.toml file as a dictionary."""

        try:
            import toml  # pyright: ignore[reportMissingModuleSource]
        except ImportError:
            # Crash if toml is not installed.
            # FIXME: This should be handled by the CLI
            print(
                "ERROR: toml is not installed. Please install it with `pip install toml` in order to read pyproject.toml files.",
                file=sys.stderr,
            )
            sys.exit(1)

        return toml.loads(filepath.read_text())
