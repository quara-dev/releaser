#!/usr/bin/env bash

set -euo pipefail

# Avoid installing dependencies each time
# uvicorn is an arbitrary package that is going to be installed
# along with the rest of the dependencies. If it's already installed
# then we can assume that the dependencies are already installed.
echo "💡 Installing requirements..."
python -m pip install -r requirements.txt --quiet
echo -e "✅ Finished installing requirements"
