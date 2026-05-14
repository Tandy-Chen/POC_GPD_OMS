# scope3_ghg (v0.2)

This project is the Python skeleton for Scope 3 reporting.

## Current scope (v0.2)

- Project structure and modules
- Input column alias mapping
- Source sheet read and validation
- Auto-locate source file by pattern
- CLI command for read validation
- Directory separation (inputs/, outputs/)

## Quick start

### Option 1: Auto-locate source file

Create `inputs/` directory in your workspace and place your source file (must match: `*.xlsx` + contain `範疇三業務管理報表`).

```bash
python -m pip install -e .
scope3-ghg validate --sheet sheet1
```

### Option 2: Explicit source path

```bash
scope3-ghg validate --input "path/to/your/file.xlsx" --sheet sheet1
```

## Directory structure

```
my_workspace/
  scope3_ghg/          (this project)
  inputs/              (source files)
  outputs/             (generated reports, v0.3+)
```

## Notes

- Files must be readable by Python libraries (not encrypted Office containers).
- Source file auto-locate: `.xlsx` + filename contains `範疇三業務管理報表`
- Output filename format: `SCOPE3_Report_GE{民國年}_各單位績效_YYYYMMDD_HHMM.xlsx`
- Example: `SCOPE3_Report_GE115_各單位績效_20260511_0843.xlsx` (2026), `SCOPE3_Report_GE116_各單位績效_20270511_0843.xlsx` (2027)
- Full report rendering is planned for v0.3.
