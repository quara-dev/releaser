from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


class PyprojectLoader:
    def load_pyproject(self, filepath: Path) -> dict[str, Any]:
        try:
            import toml  # pyright: ignore[reportMissingModuleSource]
        except ImportError:
            print(
                "ERROR: toml is not installed. Please install it with `pip install toml` in order to read pyproject.toml files.",
                file=sys.stderr,
            )
            sys.exit(1)

        return toml.loads(filepath.read_text())
