# Data Analysis with marimo and uv

Modern data analysis using reactive notebooks and fast package management.

## Quick Start

1. **Install uv** (one-time)
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows  
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Setup project**
   ```bash
   git clone <repository>
   cd <project>
   uv sync
   ```

3. **Start exploring**
   ```bash
   uv run marimo edit notebooks/explore.py
   ```

## Project Structure

```
notebooks/      # Interactive analysis (marimo .py files)
src/            # Reusable functions and classes  
data/           # Raw, processed, results (git-ignored)
tests/          # Unit tests
CLAUDE.md       # Project rules and standards
```

## Common Commands

```bash
# Edit notebooks
uv run marimo edit notebooks/explore.py

# Add packages  
uv add pandas plotly

# Run tests
uv run pytest

# Export to app
uv run marimo run notebooks/report.py --mode app
```

## Why This Stack?

- **marimo**: Reactive notebooks - no hidden state, pure Python files
- **uv**: 10-100x faster than pip, reproducible environments
- **Type hints**: Better code completion and error catching
- **Modular**: Reusable code in `src/`, notebooks stay clean

## Resources

- [marimo docs](https://docs.marimo.io/)
- [uv docs](https://docs.astral.sh/uv/)
- [Project rules](CLAUDE.md)

## For Jupyter Users

- Notebooks are `.py` files (git-friendly!)
- No more "restart kernel and run all"
- `mo.ui.slider()` instead of ipywidgets
- Convert existing notebooks: `uv run marimo convert notebook.ipynb`