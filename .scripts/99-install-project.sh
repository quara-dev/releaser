#!/usr/bin/env bash

set -euo pipefail

# Avoid installing dependencies each time
# uvicorn is an arbitrary package that is going to be installed
# along with the rest of the dependencies. If it's already installed
# then we can assume that the dependencies are already installed.
echo "💡 Installing project in development mode..."
python -m pip install -e .[dev] --quiet
echo -e "✅ Finished installing project"
