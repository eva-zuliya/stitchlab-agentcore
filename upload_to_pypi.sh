#!/bin/bash
# Upload script for PyPI
# Usage: ./upload_to_pypi.sh [testpypi|pypi]

REPO=${1:-pypi}

if [ "$REPO" = "testpypi" ]; then
    echo "Uploading to TestPyPI..."
    python3 -m twine upload --repository testpypi dist/*
else
    echo "Uploading to PyPI..."
    python3 -m twine upload dist/*
fi

