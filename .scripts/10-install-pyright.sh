#!/usr/bin/env bash

set -euo pipefail

# Install pyright
echo "💡 Installing pyright..."
python -m pip install -U pyright --quiet
echo -e "✅ Finished installing pyright"
