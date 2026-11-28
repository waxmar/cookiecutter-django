# Architecture: Core App + Features + Satellites

## Overview

This project follows a **three-tier design** that enforces **clear dependencies** and **scalability**:

| Type | Example | Description | Can exist without Core? |
|------|---------|-------------|--------------------------|
| **Core App** | `core/` | Main application with all internal features | ❌ No |
| **Features** | `core/users/`, `core/blog/` | Subpackages of Core app (logical modules) | ❌ No |
| **Satellites** | `externalsystem/` | Independent Django apps (e.g., legacy data, external systems) | ✅ **Yes** |

---

## Directory Structure

```
{{cookiecutter.project_slug}}/
├── config/                      # Django project configuration
│   ├── settings/               # Environment-specific settings
│   │   ├── base.py             # Base settings (LOCAL_APPS, AUTH_USER_MODEL)
│   │   ├── local.py            # Local settings
│   │   ├── production.py       # Production settings
│   │   └── test.py             # Test settings
│   ├── urls.py                 # Main URL routing
│   └── ...
│
├── core/                        # Core Django app
│   ├── __init__.py
│   ├── apps.py                 # Django app configuration
│   ├── users/                  # Feature: User management (Custom User Model)
│   │   ├── __init__.py
│   │   ├── models.py           # User model (AUTH_USER_MODEL)
│   │   ├── views.py
│   │   ├── admin.py
│   │   ├── urls.py
│   │   └── ...
│   ├── blog/                   # Feature: Blog functionality (example)
│   │   ├── __init__.py
│   │   └── models.py
│   └── ...
│
└── externalsystem/             # Satellite: Example of independent Django app
    ├── __init__.py
    ├── apps.py                 # Django app configuration
    ├── models.py              # Models (e.g., legacy data)
    └── migrations/             # Migrations for the satellite
```

---

## Import Rules

### Allowed Imports

| From | To | Example |
|------|-----|---------|
| **Core App** | **Features** | `from core.users.models import User` |
| **Core App** | **Satellites** | `from externalsystem.models import ExternalData` |
| **Features** | **Core App** | `from core.blog.models import Post` (within `core/`) |
| **Features** | **Features** | `from core.users.models import User` (in `core/blog/`) |

### Forbidden Imports

| From | To | Example |
|------|-----|---------|
| **Satellites** | **Core App** | `from core.users.models import User` (in `externalsystem/`) |
| **Satellites** | **Features** | `from core.blog.models import Post` (in `externalsystem/`) |
| **Satellites** | **Satellites** | `from other_satellite.models import X` |
| **Features** | **Satellites** | `from externalsystem.models import X` (in `core/users/`) |

---

## Adding New Components

### Core Features (Subpackages in `core/`)

1. **Create the subpackage:**
   ```bash
   mkdir -p core/<feature>/{models,views,urls,tests}
   touch core/<feature>/__init__.py
   ```

2. **Define the model** (example: `core/products/models.py`):
   ```python
   from django.db import models
   from core.users.models import User  # Allowed: Feature -> Feature
   
   class Product(models.Model):
       name = models.CharField(max_length=100)
       owner = models.ForeignKey(User, on_delete=models.CASCADE)  # Allowed
   ```

3. **Add views/URLs** (example: `core/products/urls.py`):
   ```python
   from django.urls import path
   from .views import ProductListView
   
   urlpatterns = [
       path("", ProductListView.as_view(), name="products"),
   ]
   ```

4. **Register URLs in Core app** (`core/urls.py`):
   ```python
   from django.urls import path, include
   
   urlpatterns = [
       path("products/", include("core.products.urls")),
   ]
   ```

Important:
- NO `apps.py` in feature subpackages!
- NO registration in `INSTALLED_APPS`!

---

### Satellite Apps (Separate Django Apps)

1. **Create the app:**
   ```bash
   uv run python manage.py startapp <satellite>
   ```

2. **Adjust `apps.py`:**
   ```python
   from django.apps import AppConfig
   
   class <Satellite>Config(AppConfig):
       name = "{{cookiecutter.project_slug}}.<satellite>"
   ```

3. **Register in `INSTALLED_APPS`** (`config/settings/base.py`):
   ```python
   LOCAL_APPS = [
       "{{cookiecutter.project_slug}}.core",  # Core app
       "{{cookiecutter.project_slug}}.<satellite>",  # Satellite
   ]
   ```

4. **Define models** (example: `externalsystem/models.py`):
   ```python
   from django.db import models
   
   # NO imports from core/ or other satellites!
   
   class ExternalData(models.Model):
       external_id = models.CharField(max_length=100, unique=True)
       data = models.JSONField()
   ```

Important:
- NO imports from `core/` or other satellites!
- Own migrations in `<satellite>/migrations/`!

---

## Enforcement

### 1. `import-linter` (Pre-commit + CI)
- Checks all import rules (see `.importlinter`).
- Blocks commits/PRs if rules are violated.
- Example error:
  ```
  externalsystem/models.py:1 - Import from core.users.models is forbidden (externalsystem -> core)
  ```

### 2. `AGENTS.md` (For AI Agents)
- Instructions for agents that generate or modify code.
- Enforces your architecture design (Core + Features + Satellites).

### 3. `check_import_linter_coverage.py` (Pre-commit Hook)
- Checks if all Django apps are registered in `.importlinter`.
- Blocks commits if an app is missing.

### 4. `add_to_importlinter.py` (Optional)
- Automatically adds new apps to `.importlinter`.
- Reduces manual effort.

---

## Checklist for New Components

| Step | Core Feature | Satellite |
|------|---------------|-----------|
| Create directory | `mkdir -p core/<feature>` | `uv run python manage.py startapp <satellite>` |
| Create `__init__.py` | Yes | Yes |
| Adjust `apps.py` | No | Yes (name = `{{cookiecutter.project_slug}}.<satellite>`) |
| Register in `INSTALLED_APPS` | No (only `core`) | Yes |
| Update `.importlinter` | Auto (via hook) | Auto (via hook) |

---

## Best Practices

1. **Core Features**: Use for all **core functionality** (User management, Blog, etc.).
2. **Satellites**: Use for **independent modules** (legacy data, external APIs, etc.).
3. **Import Rules**: Strictly follow the rules - they guarantee:
   - No circular dependencies.
   - Easy refactoring.
   - Clear architecture.
4. **Documentation**: Update `ARCHITECTURE.md` for new components.

---

## Useful Commands

```bash
# Run import linting locally
uv run import-linter --config .importlinter

# Run all pre-commit hooks (includes import linting)
pre-commit run --all-files

# Create new Core feature
mkdir -p core/<feature>/{models,views,urls,tests}
touch core/<feature>/__init__.py

# Create new Satellite app
uv run python manage.py startapp <satellite>
```
