import sys
import os
from pathlib import Path

# Set PYTHONPATH
sys.path.append(os.path.join(os.getcwd(), 'src'))

from scope3_ghg.reader import read_source_rows
from scope3_ghg.kpi import compute_performance, normalize_vendor_key, KPI_BASE_KEY, normalize_compact_text

source_file = r'C:\Tandy資料夾\APPdata\supply-chain-carbon-management\2026年_資訊技術分公司_範疇三業務管理報表_20260511.xlsx'

rows, _ = read_source_rows(input_path=source_file)

# We want uniqueVendorTotal, netZeroNotSignedCount, b_raw, kpiB_ratio, scoreB
# b_raw = unique_vendor_total - net_zero_not_signed_count

global_vendor_set = set()
for row in rows:
    if normalize_compact_text(row.kpi_key) != KPI_BASE_KEY:
        continue
    vendor_key = normalize_vendor_key(row.vendor_name_raw)
    if vendor_key:
        global_vendor_set.add(vendor_key)
unique_vendor_total = len(global_vendor_set)

net_zero_not_signed_count = sum(
    1
    for row in rows
    if normalize_compact_text(row.kpi_key) == KPI_BASE_KEY
    and "未承諾" in normalize_compact_text(row.net_zero_commitment_raw)
)

results = compute_performance(rows)

print(f"uniqueVendorTotal: {unique_vendor_total}")
print(f"netZeroNotSignedCount: {net_zero_not_signed_count}")
print(f"b_raw: {unique_vendor_total - net_zero_not_signed_count}")
print(f"kpiB_ratio: {results.kpiB_ratio}")
print(f"scoreB: {results.scoreB}")
