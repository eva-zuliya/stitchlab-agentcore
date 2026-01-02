# PyPI Publishing Checklist

## ✅ Completed

- [x] **README.md** - Created with package description, features, installation, and usage examples
- [x] **LICENSE** - MIT License file created
- [x] **pyproject.toml** - Updated with complete metadata:
  - Package name, version, description
  - Author information
  - License information
  - Keywords and classifiers
  - Project URLs (update with actual repository URLs if different)
  - Dependencies and optional dependencies
- [x] **Package Structure** - Reorganized:
  - `config.py` moved to `runtime/config.py`
  - All imports updated to use `runtime.config`
  - `runtime/__init__.py` exports all public classes
- [x] **MANIFEST.in** - Created to include README, LICENSE, and assets
- [x] **.gitignore** - Already exists with proper exclusions

## 📝 Before Publishing

1. **Update Project URLs** in `pyproject.toml` if your repository URL is different:
   ```toml
   [project.urls]
   Homepage = "https://github.com/your-org/stitchlab-agentcore"
   Repository = "https://github.com/your-org/stitchlab-agentcore"
   Issues = "https://github.com/your-org/stitchlab-agentcore/issues"
   ```

2. **Update Author Email** in `pyproject.toml` if needed:
   ```toml
   authors = [
       {name = "StitchLab", email = "your-email@stitchlab.ai"}
   ]
   ```

3. **Test the Build**:
   ```bash
   # Clean previous builds
   rm -rf build/ dist/ *.egg-info/
   
   # Build the package
   pip install build
   python -m build
   
   # Verify the build
   twine check dist/*
   ```

4. **Test Installation Locally**:
   ```bash
   pip install dist/stitchlab_agentcore-0.1.0-py3-none-any.whl
   python -c "from runtime import AgentFactory, StitchLabAgentCoreApp; print('Import successful!')"
   ```

5. **Test on TestPyPI** (recommended):
   ```bash
   # Upload to TestPyPI first
   pip install twine
   twine upload --repository testpypi dist/*
   
   # Test install from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ stitchlab-agentcore
   ```

## 🚀 Publishing Steps

1. **Get PyPI API Token**:
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token
   - Save it securely

2. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```
   - Username: `__token__`
   - Password: Your API token

3. **Verify Publication**:
   - Check https://pypi.org/project/stitchlab-agentcore/
   - Test installation: `pip install stitchlab-agentcore`

## 📦 Package Contents

The package includes:
- `runtime/` - Main package with:
  - `__init__.py` - Exports AgentFactory, StitchLabAgentCoreApp, GlobalConfig, BaseSettings
  - `app.py` - StitchLabAgentCoreApp class
  - `factory.py` - AgentFactory class
  - `config.py` - GlobalConfig and BaseSettings classes
- `README.md` - Package documentation
- `LICENSE` - MIT License
- `assets/` - Tiktoken cache assets (if needed)

## 🔄 Version Updates

When updating the version:
1. Update `version` in `pyproject.toml`
2. Rebuild: `python -m build`
3. Upload: `twine upload dist/*`

## 📚 Documentation

- See `PUBLISHING.md` for detailed publishing instructions
- See `README.md` for package usage documentation



