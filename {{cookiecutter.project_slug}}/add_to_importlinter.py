#!/usr/bin/env python3
"""Automatically add new Django apps to .importlinter."""
import re
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


def extract_existing_layers(importlinter_path):
    """Extract existing layers from .importlinter."""
    existing_layers = set()
    if importlinter_path.exists():
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
                    layer_name = line.split("=")[0].strip()
                    existing_layers.add(layer_name)
    return existing_layers


def main():
    """Main function: Add missing apps to .importlinter."""
    apps = extract_apps_from_settings()
    importlinter_path = Path(".importlinter")
    existing_layers = extract_existing_layers(importlinter_path)
    
    new_layers = []
    for app in apps:
        # Skip third-party packages
        if app.startswith("django") or app.startswith("allauth") or app.startswith("crispy"):
            continue
        
        # Extract layer name (last part of the path)
        layer_name = app.split(".")[-1]
        
        # Check if layer already exists
        if layer_name not in existing_layers:
            # For Core app: Handle specially
            if app.endswith(".core") or "core" in app:
                if layer_name == "core":
                    new_layers.append(f"core = {app}")
                    existing_layers.add("core")
                elif "." in app:
                    parts = app.split(".")
                    if len(parts) >= 3 and parts[-2] == "core":
                        feature_name = parts[-1]
                        if feature_name not in existing_layers:
                            new_layers.append(f"{feature_name} = {app}.{feature_name}")
                            existing_layers.add(feature_name)
            else:
                # Satellite apps
                new_layers.append(f"{layer_name} = {app}")
                existing_layers.add(layer_name)
    
    if new_layers:
        # Update .importlinter file
        if not importlinter_path.exists():
            with open(importlinter_path, "w") as f:
                f.write("[importlinter]\n")
                f.write("root_package = {{cookiecutter.project_slug}}\n\n")
                f.write("[layers]\n")
        
        # Check if [layers] exists
        with open(importlinter_path, "r") as f:
            content = f.read()
        
        if "[layers]" not in content:
            content += "\n[layers]\n"
        
        # Add new layers
        with open(importlinter_path, "a") as f:
            for layer in new_layers:
                f.write(f"\n{layer}")
        
        print(f"✅ Added the following layers to .importlinter:")
        for layer in new_layers:
            print(f"   {layer}")
    else:
        print("✅ All apps are already registered in .importlinter.")


if __name__ == "__main__":
    main()
