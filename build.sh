#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Optional: Run any database migrations or setup scripts here
# python crear_usuario_admin.py
