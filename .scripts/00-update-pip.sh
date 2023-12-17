#!/usr/bin/env bash

set -euo pipefail

function install() {
    python -m pip install --upgrade pip setuptools wheel --quiet
}

# Update pip and build-related packages
echo "💡 Updating pip and installing build-related packages..."
install
echo -e "✅ Finished updating pip and installing build-related packages"
