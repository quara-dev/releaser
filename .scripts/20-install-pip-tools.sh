#!/usr/bin/env bash

set -euo pipefail

# Install pip-tools
echo "💡 Installing pip-tools..."
python -m pip install -U pip-tools --quiet
echo -e "✅ Finished installing pip-tools"
