# Release Instructions

## Steps to publish a new version to PyPI

### 1. Update version number

Edit `pyproject.toml` / tradestation/__init__.py and update the version:
```toml
version = "1.1.0"  # Change to new version
```

### 2. Update lock file

```bash
uv sync --extra dev
```

This updates `uv.lock` to reflect the new version and ensures build tools are installed.

### 3. Commit and tag

```bash
git add pyproject.toml tradestation/__init__.py uv.lock
git commit -m "Bump version to 1.1.0"
git tag v1.1.0
git push && git push --tags
```

### 4. Clean old builds

**Unix/Linux/macOS:**
```bash
rm -rf dist/
```

**Windows PowerShell:**
```powershell
Remove-Item -Recurse -Force dist/
```

### 5. Build package

```bash
.venv\Scripts\python.exe -m build
```

### 6. Upload to PyPI

```bash
.venv\Scripts\python.exe -m twine upload dist/* -u __token__ -p pypi-YOUR_TOKEN_HERE
```

Or without token in command (will prompt):
```bash
.venv\Scripts\python.exe -m twine upload dist/*
# Username: __token__
# Password: pypi-YOUR_TOKEN_HERE
```

## PyPI Token

- Create/manage tokens at: https://pypi.org/manage/account/token/
- Tokens start with `pypi-`
- Store securely, do not commit to git

## Verify

After upload, check: https://pypi.org/project/tradestation-downloader/
