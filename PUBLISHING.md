# Publishing to PyPI

This guide explains how to publish `stitchlab-agentcore` to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **TestPyPI Account** (optional, for testing): Create an account at https://test.pypi.org/account/register/
3. **API Token**: Generate an API token at https://pypi.org/manage/account/token/ (or TestPyPI equivalent)

## Installation

Install the required build tools:

```bash
pip install build twine
```

## Building the Package

1. **Clean previous builds**:
   ```bash
   rm -rf build/ dist/ *.egg-info/
   ```

2. **Build the package**:
   ```bash
   python -m build
   ```

   This will create:
   - `dist/stitchlab-agentcore-0.1.0.tar.gz` (source distribution)
   - `dist/stitchlab_agentcore-0.1.0-py3-none-any.whl` (wheel distribution)

## Testing the Build

Before publishing to PyPI, test your package:

1. **Test installation locally**:
   ```bash
   pip install dist/stitchlab_agentcore-0.1.0-py3-none-any.whl
   ```

2. **Test on TestPyPI** (recommended):
   ```bash
   # Upload to TestPyPI
   twine upload --repository testpypi dist/*
   
   # Test install from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ stitchlab-agentcore
   ```

## Publishing to PyPI

1. **Check the package**:
   ```bash
   twine check dist/*
   ```

2. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

   You'll be prompted for:
   - Username: `__token__`
   - Password: Your PyPI API token

   Or use environment variables:
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=your-api-token-here
   twine upload dist/*
   ```

## Updating the Version

Before publishing a new version:

1. Update the version in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # Increment as needed
   ```

2. Update the version in `runtime/__init__.py` if you have a `__version__` variable (optional)

3. Rebuild and upload:
   ```bash
   rm -rf build/ dist/ *.egg-info/
   python -m build
   twine upload dist/*
   ```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Troubleshooting

- **"Package already exists"**: Increment the version number
- **"Invalid distribution"**: Run `twine check dist/*` to see errors
- **"Authentication failed"**: Verify your API token is correct
- **"Missing files"**: Check `MANIFEST.in` includes all necessary files

## Post-Publishing

After publishing:

1. Verify the package on PyPI: https://pypi.org/project/stitchlab-agentcore/
2. Test installation:
   ```bash
   pip install stitchlab-agentcore
   ```
3. Update documentation if needed
4. Tag the release in git:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```



