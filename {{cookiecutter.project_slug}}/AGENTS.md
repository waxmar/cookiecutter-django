# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Import Linting Rules

This project uses `import-linter` to enforce architecture rules for satellite apps:

- **`{{cookiecutter.project_slug}}/`** is the core application
- **`users/`** is a satellite app (independent Django app)
- **Import Rules (enforced by `import-linter`)**:
  - Core app can import from satellites: `from users.models import User`
  - Satellites MUST NOT import from core or other satellites: `users/` must not import from `{{cookiecutter.project_slug}}/`

When adding new satellite apps, update `.importlinter` to include them as layers.
Helper scripts for this live in `bin/`:

```bash
python bin/importlinter_add_apps.py           # register new apps as layers
python bin/importlinter_check_coverage.py     # verify all apps are registered
```
