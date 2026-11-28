"""
Core Django App Configuration

This app contains all internal features of the project as subpackages:
- core/users/ (User management)
- core/blog/ (Blog functionality)
- ... (other features)

Satellite apps (e.g., externalsystem/) are SEPARATE Django apps and
MUST NOT depend on this app.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "{{cookiecutter.project_slug}}.core"
    verbose_name = "Core Application"
