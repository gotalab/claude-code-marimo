# CLAUDE.md - Data Analysis Project Rules

## Project Philosophy

This is a modern data analysis project that prioritizes:
- **Reproducibility**: Same code, same results, every time
- **Reactivity**: Changes propagate automatically
- **Simplicity**: Less code, less bugs
- **Speed**: Fast iteration cycles

## Core Technology Choices

### Why marimo (not Jupyter)
- **Pure Python files**: Git-friendly, no JSON merge conflicts
- **Reactive execution**: No manual cell re-running, no hidden state
- **Built-in UI elements**: Interactive analysis without callbacks
- **SQL integration**: Native DuckDB support for large data

### Why uv (not pip/conda)
- **10-100x faster**: Instant package installation
- **Reproducible**: Lock files ensure exact environments
- **Simple**: One tool for packages, environments, and Python versions
- **Modern**: Rust-based performance for data science scale

## Project Rules

### 1. File Organization
- **Notebooks are for exploration and reporting only**
- **All reusable code goes in `src/` modules**
- **No numbered prefixes** (not 01_analysis.py)
- **One purpose per file**

### 2. marimo Specifics
```bash
# Always use uv run
uv run marimo edit notebooks/analysis.py  # ✅
marimo edit notebooks/analysis.py         # ❌
```

### 3. No Code Duplication
- If you write it twice, it belongs in a module
- Notebooks import from `src/`, never copy code
- Use functions, not copy-paste

### 4. Dependencies
- Add via `uv add` (not pip install)
- Commit `uv.lock` always
- Document why each package is needed

## Coding Standards

### Python Style
- **Type hints required** on all functions
- **Docstrings required** for public functions
- **Black** for formatting (no debates)
- **Ruff** for linting

### Imports
```python
# Group order: standard → third-party → local
from pathlib import Path
from typing import Optional

import pandas as pd
import marimo as mo

from src.config import DATA_DIR
```

### Data Handling
- Use `pathlib.Path`, not string paths
- Use `pd.DataFrame` type hints
- Validate data early with explicit checks
- Prefer Parquet for processed data

### Error Messages
```python
# Be helpful
raise ValueError(
    f"Column 'price' not found. "
    f"Available columns: {df.columns.tolist()}"
)
```

## marimo Best Practices

### Cell Design
- Small, focused cells
- Use `mo.stop()` for conditional execution
- Let reactivity handle updates

### UI Elements
```python
# Always label and set defaults
slider = mo.ui.slider(
    start=0, 
    stop=100, 
    value=50,
    label="Threshold (%)"  # Required!
)
```

### Performance
- Use SQL for large data filtering
- Cache expensive computations
- Lazy execution for heavy notebooks

### Visualization
```python
# Interactive dataframes (default shows 5 rows)
mo.ui.dataframe(df, page_size=10)  # For main datasets only

# Plotly charts work normally
import plotly.express as px
chart = px.bar(df, ...)  # Just display the chart

# For interactive selections, prefer Altair
mo.ui.altair_chart(...)  # More features than mo.ui.plotly()
```

### Running notebooks
- **As app**: `uv run marimo run notebook.py` (interactive, no code shown)
- **As script**: `uv run python notebook.py` (for automation, side effects)
  - Print statements and console output appear in terminal
  - Access args via `sys.argv` like any Python script
  - Use `argparse` or other CLI libraries normally
  - Perfect for scheduled jobs, CI/CD pipelines
- **With args**: `uv run marimo run notebook.py -- --param value`
- **Export**: Multiple formats available (HTML, WASM, ipynb)

### Script execution pattern
```python
# In notebook, handle both modes
import marimo as mo

if mo.running_in_notebook():
    # Interactive defaults for marimo edit/run
    date = "2024-01-01"
else:
    # Get from command line for script execution
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    date = args.date
```

## Workflow

1. **Explore** in `notebooks/explore.py`
2. **Extract** common code to `src/`
3. **Test** with pytest
4. **Document** in docstrings
5. **Share** via marimo app mode or export
6. **Automate** by running as scripts

### Automation examples
```bash
# Daily report generation
uv run python notebooks/daily_report.py --date $(date +%Y-%m-%d)

# Batch processing
uv run python notebooks/process_data.py --input data/raw/*.csv

# CI/CD pipeline
uv run python notebooks/validate_data.py && echo "Data validation passed"
```

## Anti-patterns to Avoid

- ❌ Creating "backup" or "v2" notebooks
- ❌ Long notebooks with mixed purposes  
- ❌ Installing packages outside uv
- ❌ Committing data files
- ❌ Global variables in modules
- ❌ Untested data transformations

## Quick Reference

### Essential marimo commands
```bash
# Edit notebook
uv run marimo edit notebooks/explore.py

# Edit with file watching (real-time updates from external editor)
uv run marimo edit notebooks/explore.py --watch

# Run as app (hides code)
uv run marimo run notebooks/report.py

# Run as app with file watching (auto-refresh on changes)
uv run marimo run notebooks/report.py --watch

# Run as script
uv run python notebooks/analysis.py

# Pass arguments
uv run marimo run notebooks/report.py -- --date 2024-01-01
uv run python notebooks/report.py --date 2024-01-01  # As script

# Convert from Jupyter
uv run marimo convert old.ipynb -o notebooks/new.py

# Export formats
uv run marimo export html notebooks/report.py -o report.html
uv run marimo export html-wasm notebooks/app.py -o app.html
uv run marimo export script notebooks/analysis.py -o analysis_script.py

# Interactive tutorials
uv run marimo tutorial intro
```

### Package management
```bash
# Add packages
uv add pandas plotly "marimo[sql]"

# Add dev tools  
uv add --dev pytest ruff mypy

# Update packages
uv sync

# Performance tip: Install watchdog for faster file watching
uv add --dev watchdog
```

## Project-Specific Rules

[Add your domain-specific rules here]

- Data sources: 
- Key metrics:
- Business logic:
- Naming conventions: