# COMP5112 Group 7 - Submission Checklist

## Files Ready for Submission

### 1. Source Code Archive
**File**: `comp5112_group7_source_code.zip` (123 KB)

**Contents**:
- ✅ All source code (`src/` directory)
- ✅ All scripts (`scripts/` directory)
- ✅ Documentation (`docs/`, README.md, Technical Reports)
- ✅ Configuration files (`config/`, `env.template`)
- ✅ Requirements file (`requirements.txt`)

**Excluded** (as appropriate):
- ❌ Database files (*.db)
- ❌ Cache files (__pycache__)
- ❌ Virtual environment (.venv)
- ❌ Large data files
- ❌ Generated images and logs

**How to recreate**:
```bash
python package_source_code.py
# or
./package_source_code.sh
```

### 2. Dataset Archive
**Directory**: `dataset_export/`

**Contents**:
- `api_products.json` (93.43 MB) - 43,226 products
- `social_media_products.json` (33.54 MB) - 26,262 posts
- `search_queries.json` - 38 queries
- `collection_logs.json` - 370 logs
- `dataset_summary.json` - Summary statistics
- `README.md` - Dataset documentation
- `SUBMISSION_GUIDE.md` - Submission instructions

**How to package**:
```bash
cd dataset_export
zip -r ../dataset_export.zip .
# or
tar -czf ../dataset_export.tar.gz .
```

## Submission Steps

### Step 1: Verify Files
```bash
# Check source code zip
unzip -l comp5112_group7_source_code.zip

# Check dataset directory
ls -lh dataset_export/
```

### Step 2: Package Dataset (if needed)
If your professor wants the dataset as a zip file:
```bash
cd dataset_export
zip -r ../dataset_export.zip .
cd ..
```

### Step 3: Submit
Submit the following to your professor:

1. **Source Code**: `comp5112_group7_source_code.zip`
2. **Dataset**: Either:
   - The entire `dataset_export/` directory, OR
   - `dataset_export.zip` (if you created it)

## File Sizes Summary

- **Source Code**: 123 KB (compressed)
- **Dataset**: ~127 MB (uncompressed), ~30-50 MB (compressed)

## Verification

### Verify Source Code
```bash
# Extract and check
unzip -q comp5112_group7_source_code.zip -d /tmp/check_source
ls -R /tmp/check_source/comp5112_group7_project/
```

### Verify Dataset
```bash
# Test import
python scripts/utilities/import_dataset.py --input-dir dataset_export --reset
```

## Notes

- The source code zip is ready to submit as-is
- The dataset can be submitted as a directory or compressed archive
- Both packages are self-contained and include documentation
- The dataset includes import scripts for reproducibility

## Quick Commands

```bash
# Create source code zip
python package_source_code.py

# Create dataset zip (optional)
cd dataset_export && zip -r ../dataset_export.zip . && cd ..

# Verify source code
unzip -l comp5112_group7_source_code.zip | head -20

# Check file sizes
ls -lh comp5112_group7_source_code.zip dataset_export/
```

