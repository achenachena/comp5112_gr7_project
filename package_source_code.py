#!/usr/bin/env python3
"""
Package Source Code for Submission

This script creates a clean zip file of the source code, excluding
database files, cache, virtual environment, and other unnecessary files.

Usage:
    python package_source_code.py
"""

import os
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

# Project root directory
PROJECT_ROOT = Path(__file__).parent
ZIP_NAME = "comp5112_group7_source_code.zip"

# Patterns to exclude
EXCLUDE_PATTERNS = [
    # Database files
    '*.db', '*.db-shm', '*.db-wal', '*.sqlite', '*.sqlite3',
    # Python cache
    '__pycache__', '*.pyc', '*.pyo', '*.pyd',
    # Virtual environments
    '.venv', 'venv', 'env', 'ENV',
    # Environment files
    '.env', '.env.*',
    # IDE files
    '.vscode', '.idea',
    # OS files
    '.DS_Store', 'Thumbs.db',
    # Logs and generated files
    '*.log', '*.png', '*.jpg', '*.jpeg', '*.pdf', '*.csv',
    # Data directories
    'dataset_export', 'data/*.db*', 'data/*.json',
    'data/checkpoints', 'data/exports', 'data/results',
    # Git
    '.git', '.gitignore',
    # Build artifacts
    'build', 'dist', '*.egg-info', '*.egg',
    # Testing
    '.pytest_cache', '.coverage', 'htmlcov',
    # Jupyter
    '.ipynb_checkpoints', '*.ipynb',
    # Temporary files
    '*.swp', '*.swo', '*.tmp',
    # Large documents (keep markdown, exclude docx)
    '*.docx',
    # Package script itself
    'package_source_code.sh', 'package_source_code.py',
]

# Directories to always include (even if empty)
INCLUDE_DIRS = [
    'src', 'scripts', 'docs', 'config', 'data',
    'src/ecommerce_search',
    'src/ecommerce_search/algorithms',
    'src/ecommerce_search/database',
    'src/ecommerce_search/evaluation',
    'src/ecommerce_search/utils',
    'src/ecommerce_search/web',
    'src/ecommerce_search/web/static',
    'src/ecommerce_search/web/templates',
    'scripts/analysis',
    'scripts/data_collection',
    'scripts/utilities',
]


def should_exclude(file_path: Path) -> bool:
    """Check if a file or directory should be excluded."""
    path_str = str(file_path)
    
    # Check against exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str or file_path.match(pattern):
            return True
    
    # Exclude hidden files (except important ones)
    if file_path.name.startswith('.') and file_path.name not in ['.gitattributes']:
        return True
    
    return False


def should_include(file_path: Path) -> bool:
    """Check if a file should be included."""
    # If it's not excluded, include it (default to include)
    # This ensures we include all source files, configs, docs, etc.
    
    # Always include these important files
    important_files = [
        'README.md', 'requirements.txt', 'env.template',
        'COMP5112_Group7_Technical_Report.md',
        'COMP5112_Group7_IEEE_Paper.md',
        '.gitattributes',
    ]
    
    if file_path.name in important_files:
        return True
    
    # Include common source/documentation file types
    if file_path.suffix in ['.py', '.md', '.txt', '.html', '.css', '.js', '.json', '.template', '.sh']:
        return True
    
    # Include empty __init__.py files (they might not have extension check)
    if file_path.name == '__init__.py':
        return True
    
    # Include config directory files
    if 'config' in str(file_path):
        return True
    
    # Default: include if not explicitly excluded
    return True


def create_source_zip():
    """Create a zip file with the source code."""
    print("📦 Packaging source code for submission...")
    print("")
    
    zip_path = PROJECT_ROOT / ZIP_NAME
    
    # Remove existing zip if it exists
    if zip_path.exists():
        zip_path.unlink()
    
    included_count = 0
    excluded_count = 0
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through all files
        for root, dirs, files in os.walk(PROJECT_ROOT):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
            
            root_path = Path(root)
            
            # Skip if root directory itself should be excluded
            if should_exclude(root_path):
                continue
            
            # Process files
            for file in files:
                file_path = root_path / file
                
                # Skip if should be excluded
                if should_exclude(file_path):
                    excluded_count += 1
                    continue
                
                # Include if it's an important file or matches include criteria
                if should_include(file_path):
                    # Calculate relative path
                    try:
                        arcname = file_path.relative_to(PROJECT_ROOT)
                        zipf.write(file_path, arcname)
                        included_count += 1
                    except ValueError:
                        # File is outside project root, skip
                        excluded_count += 1
                        continue
    
    # Get file size
    file_size = zip_path.stat().st_size
    size_mb = file_size / (1024 * 1024)
    size_kb = file_size / 1024
    
    if size_mb >= 1:
        size_str = f"{size_mb:.2f} MB"
    else:
        size_str = f"{size_kb:.0f} KB"
    
    print("✅ Source code packaged successfully!")
    print(f"📁 File: {ZIP_NAME}")
    print(f"📊 Size: {size_str}")
    print(f"📄 Files included: {included_count}")
    print(f"🚫 Files excluded: {excluded_count}")
    print("")
    print("Contents included:")
    print("  ✓ Source code (src/)")
    print("  ✓ Scripts (scripts/)")
    print("  ✓ Documentation (docs/, README.md, Technical Reports)")
    print("  ✓ Configuration files (config/, env.template)")
    print("  ✓ Requirements (requirements.txt)")
    print("")
    print("Contents excluded:")
    print("  ✗ Database files (*.db)")
    print("  ✗ Cache files (__pycache__)")
    print("  ✗ Virtual environment (.venv)")
    print("  ✗ Large data files (dataset_export/)")
    print("  ✗ Generated images and logs")
    print("  ✗ Word documents (*.docx)")


if __name__ == "__main__":
    try:
        create_source_zip()
    except Exception as e:
        print(f"❌ Error creating zip file: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

