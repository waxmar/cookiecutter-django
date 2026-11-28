"""
External System Django App Configuration

This is a SATELLITE app:
- Can exist independently from the Core app
- Must NOT import from Core or other satellites
- Only used by Core app (import flow: core -> externalsystem)
"""

from django.apps import AppConfig


class ExternalsystemConfig(AppConfig):
    name = "{{cookiecutter.project_slug}}.externalsystem"
    verbose_name = "External System"
