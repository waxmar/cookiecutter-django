#!/usr/bin/env python3
"""Check that all Django apps are registered in .importlinter."""
import re
import sys
from pathlib import Path


def extract_apps_from_settings():
    """Extract all Django apps from settings/base.py."""
    settings_path = Path("config/settings/base.py")
    apps = []
    if not settings_path.exists():
        print("⚠️  config/settings/base.py not found!")
        return []
    
    with open(settings_path) as f:
        in_local_apps = False
        in_installed_apps = False
        for line in f:
            line = line.strip()
            if line.startswith("LOCAL_APPS = ["):
                in_local_apps = True
                continue
            if line.startswith("INSTALLED_APPS = ["):
                in_installed_apps = True
                continue
            if in_local_apps or in_installed_apps:
                if line == "]":
                    in_local_apps = False
                    in_installed_apps = False
                    continue
                # Extract app names
                matches = re.findall(r'"([^"]+)"', line)
                apps.extend(matches)
                matches = re.findall(r"'([^']+)'", line)
                apps.extend(matches)
    return apps


def extract_layers_from_importlinter():
    """Extract all layers from .importlinter."""
    importlinter_path = Path(".importlinter")
    layers = []
    if not importlinter_path.exists():
        return []
    
    with open(importlinter_path) as f:
        in_layers = False
        for line in f:
            line = line.strip()
            if line == "[layers]":
                in_layers = True
                continue
            if in_layers and line.startswith("[") and line != "[layers]":
                in_layers = False
                continue
            if in_layers and "=" in line:
                layer = line.split("=")[0].strip()
                layers.append(layer)
    return layers


def main():
    """Main function: Check if all apps are registered in .importlinter."""
    apps = extract_apps_from_settings()
    layers = extract_layers_from_importlinter()
    
    # Filter only local apps (not third-party packages)
    local_apps = [
        app for app in apps 
        if not "." in app or app.startswith("{{cookiecutter.project_slug}}.")
    ]
    
    missing_apps = []
    for app in local_apps:
        # Check if the app or a part of it is in layers
        found = False
        for layer in layers:
            if app in layer or layer.endswith(app.split(".")[-1]):
                found = True
                break
            if app == layer:
                found = True
                break
        if not found:
            missing_apps.append(app)
    
    if missing_apps:
        print("❌ ERROR: The following Django apps are not registered in .importlinter:")
        for app in missing_apps:
            print(f"   - {app}")
        print("\n📌 Please add them to .importlinter, for example:")
        for app in missing_apps:
            app_name = app.split(".")[-1] if "." in app else app
            print(f"   [layers]\n   {app_name} = {app}")
        sys.exit(1)
    else:
        print("✅ All Django apps are registered in .importlinter.")
        sys.exit(0)


if __name__ == "__main__":
    main()
