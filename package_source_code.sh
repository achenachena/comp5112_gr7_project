#!/bin/bash

# Script to package source code for submission
# Excludes database files, cache, virtual environment, and other unnecessary files

ZIP_NAME="comp5112_group7_source_code.zip"
TEMP_DIR=$(mktemp -d)

echo "📦 Packaging source code for submission..."
echo ""

# Copy files to temp directory, excluding unwanted files
rsync -av \
  --exclude='*.db' \
  --exclude='*.db-shm' \
  --exclude='*.db-wal' \
  --exclude='*.sqlite' \
  --exclude='*.sqlite3' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='*.pyd' \
  --exclude='.venv' \
  --exclude='venv' \
  --exclude='env' \
  --exclude='ENV' \
  --exclude='.env' \
  --exclude='.env.*' \
  --exclude='.vscode' \
  --exclude='.idea' \
  --exclude='.DS_Store' \
  --exclude='*.log' \
  --exclude='*.png' \
  --exclude='*.jpg' \
  --exclude='*.jpeg' \
  --exclude='*.pdf' \
  --exclude='*.csv' \
  --exclude='dataset_export' \
  --exclude='data/*.db*' \
  --exclude='data/*.json' \
  --exclude='data/checkpoints' \
  --exclude='data/exports' \
  --exclude='data/results' \
  --exclude='.git' \
  --exclude='.gitignore' \
  --exclude='*.swp' \
  --exclude='*.swo' \
  --exclude='.pytest_cache' \
  --exclude='.coverage' \
  --exclude='htmlcov' \
  --exclude='build' \
  --exclude='dist' \
  --exclude='*.egg-info' \
  --exclude='*.egg' \
  --exclude='.ipynb_checkpoints' \
  --exclude='*.ipynb' \
  --exclude='comp5112_group7_tech_report.docx' \
  --exclude='Comparative Study of Search Algorithms in Ecommerce.docx' \
  . "$TEMP_DIR/comp5112_group7_project"

# Create zip file
cd "$TEMP_DIR"
zip -r "$ZIP_NAME" comp5112_group7_project/ > /dev/null

# Move zip to project root
mv "$ZIP_NAME" "$OLDPWD/"

# Cleanup
cd "$OLDPWD"
rm -rf "$TEMP_DIR"

# Get file size
FILE_SIZE=$(du -h "$ZIP_NAME" | cut -f1)

echo "✅ Source code packaged successfully!"
echo "📁 File: $ZIP_NAME"
echo "📊 Size: $FILE_SIZE"
echo ""
echo "Contents included:"
echo "  ✓ Source code (src/)"
echo "  ✓ Scripts (scripts/)"
echo "  ✓ Documentation (docs/, README.md)"
echo "  ✓ Configuration files (config/, env.template)"
echo "  ✓ Requirements (requirements.txt)"
echo ""
echo "Contents excluded:"
echo "  ✗ Database files (*.db)"
echo "  ✗ Cache files (__pycache__)"
echo "  ✗ Virtual environment (.venv)"
echo "  ✗ Large data files (dataset_export/)"
echo "  ✗ Generated images and logs"

