"""Matrix report renderer."""

from __future__ import annotations

from datetime import datetime

from openpyxl import Workbook

from ..aggregators import (
    aggregate_by_dept,
    compute_unique_vendor_counts_for_carbon_kpi,
    resolve_department,
    resolve_status,
)
from ..config import CONTRACT_STATUS_7, DEPT_ORDER, KPI_BASE_KEY
from ..models import ContractRow
from ..normalize import normalize_compact_text
from .style import (
    append_merged_note,
    append_stat_date,
    apply_body_borders,
    apply_header_style,
    apply_standard_layout,
    auto_fit_columns,
)


def _bool_like(value: str) -> bool:
    normalized = normalize_compact_text(value).lower()
    return normalized in {"y", "yes", "true", "1", "是", "有", "已簽署"}


MATRIX_ROW_DEFINITIONS = [
    "已簽3000萬元(含)以上列管契約案",
    *CONTRACT_STATUS_7,
    "自主盤查契約",
    "盤查範圍契約(持續盤查契約)",
    "資分碳智雲上載契約案",
    "不重複供應商數",
    "未簽署淨零承諾契約案",
]

UNSUITABLE_STATUSES = {
    "請/採購人員認為不適合進行(數位內容採購)",
    "請/採購人員認為不適合進行",
}
APPROVED_STATUS = "資料通過顧問審核標準"


def _build_metric_values(rows: list[ContractRow], row_name: str, kpi_base_rows: list[ContractRow]) -> list[object]:
    if row_name == "不重複供應商數":
        dept_counts, total_unique = compute_unique_vendor_counts_for_carbon_kpi(rows, KPI_BASE_KEY)
        return [*dept_counts, total_unique, 0]

    if row_name == "已簽3000萬元(含)以上列管契約案":
        dept_counts, total_count, total_amount_m = aggregate_by_dept(rows, lambda row: row.contract_amount >= 30_000_000, False)
    elif row_name in CONTRACT_STATUS_7:
        exclude_unsuitable = "不適合進行" not in row_name
        dept_counts, total_count, total_amount_m = aggregate_by_dept(
            kpi_base_rows,
            lambda row, target=row_name: resolve_status(row.contract_status_raw) == target,
            exclude_unsuitable,
        )
    elif row_name == "自主盤查契約":
        dept_counts, total_count, total_amount_m = aggregate_by_dept(
            rows,
            lambda row: normalize_compact_text(row.kpi_key) == "自主盤查契約",
            True,
        )
    elif row_name == "盤查範圍契約(持續盤查契約)":
        dept_counts, total_count, total_amount_m = aggregate_by_dept(
            rows,
            lambda row: not (
                resolve_status(row.contract_status_raw) == APPROVED_STATUS
                or resolve_status(row.contract_status_raw) in UNSUITABLE_STATUSES
                or normalize_compact_text(row.kpi_key) == "自主盤查契約"
            ),
            False,
        )
    elif row_name == "資分碳智雲上載契約案":
        dept_counts, total_count, total_amount_m = aggregate_by_dept(
            rows,
            lambda row: normalize_compact_text(row.kpi_key) == KPI_BASE_KEY,
            True,
        )
    elif row_name == "未簽署淨零承諾契約案":
        dept_counts, total_count, total_amount_m = aggregate_by_dept(
            rows,
            lambda row: "未簽" in normalize_compact_text(row.net_zero_commitment_raw),
            True,
        )
    else:
        dept_counts, total_count, total_amount_m = [0 for _ in DEPT_ORDER], 0, 0.0

    return [*dept_counts, total_count, total_amount_m]


def _status_count_check_rows(matrix_rows: list[tuple[str, list[object]]], kpi_base_rows: list[ContractRow]) -> list[list[object]]:
    status_rows = [values for label, values in matrix_rows if label in CONTRACT_STATUS_7]
    status_sum_by_dept = [sum(int(row[idx]) for row in status_rows) for idx in range(len(DEPT_ORDER))]
    unclassified_rows = [
        row
        for row in kpi_base_rows
        if resolve_status(row.contract_status_raw) in CONTRACT_STATUS_7
        and resolve_department(row.requester_unit) == "未分類(單位)"
    ]
    unclassified_count = len(unclassified_rows)
    total_check_sum = sum(status_sum_by_dept) + unclassified_count
    return [
        ["【檢核】狀態合計（部門件數）", *status_sum_by_dept, total_check_sum, ""],
        ["【檢核】未落入部門統計（未分類-異常清單）", *([""] * len(DEPT_ORDER)), unclassified_count, ""],
    ]


def _amount_check_rows(rows: list[ContractRow], kpi_base_rows: list[ContractRow]) -> list[list[object]]:
    dept_amount_m = []
    for dept in DEPT_ORDER:
        dept_amount_m.append(round(sum(row.contract_amount for row in rows if resolve_department(row.requester_unit) == dept) / 1_000_000, 2))
    total_dept_amount_m = round(sum(dept_amount_m), 2)
    unclassified_rows = [
        row
        for row in kpi_base_rows
        if resolve_status(row.contract_status_raw) in CONTRACT_STATUS_7
        and resolve_department(row.requester_unit) == "未分類(單位)"
    ]
    unclassified_amount_m = round(sum(row.contract_amount for row in unclassified_rows) / 1_000_000, 2)
    return [
        ["【檢核】各部門金額合計", *dept_amount_m, total_dept_amount_m, ""],
        ["【檢核】未落入部門統計金額（未分類-異常清單）", *([""] * len(DEPT_ORDER)), unclassified_amount_m, ""],
    ]


def render_matrix_report(workbook: Workbook, rows: list[ContractRow], source_name: str, now: datetime | None = None) -> None:
    ws = workbook.create_sheet("統計分析_矩陣")
    ws.append(["管控項目", *DEPT_ORDER, "契約總計", "金額總計(百萬元)"])
    header_row = 1
    apply_header_style(ws, header_row)

    kpi_base_rows = [row for row in rows if normalize_compact_text(row.kpi_key) == KPI_BASE_KEY]
    metrics = [(row_name, _build_metric_values(rows, row_name, kpi_base_rows)) for row_name in MATRIX_ROW_DEFINITIONS]

    for label, values in metrics:
        ws.append([label, *values])

    ws.append([])
    ws.append(["檢核（依契約狀態合計）"])
    for row in _status_count_check_rows(metrics, kpi_base_rows):
        ws.append(row)

    ws.append([])
    ws.append(["檢核（部門金額合計，百萬元）"])
    for row in _amount_check_rows(rows, kpi_base_rows):
        ws.append(row)

    content_end_row = ws.max_row
    apply_body_borders(ws, start_row=header_row, end_row=content_end_row)
    append_merged_note(ws, "附註：計算口徑與稽核重點請參考「口徑要項彙總」工作表。")
    append_stat_date(ws, now=now)
    apply_standard_layout(ws, "A2")
    auto_fit_columns(ws, max_row=content_end_row)
