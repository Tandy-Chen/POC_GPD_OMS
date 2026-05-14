"""Exception report renderer."""

from __future__ import annotations

from datetime import datetime

from openpyxl import Workbook

from ..aggregators import resolve_department, resolve_status
from ..models import ContractRow
from .style import append_stat_date, apply_body_borders, apply_header_style, apply_standard_layout, auto_fit_columns

WAITING_STATUS = "等待供應商上傳第一筆資料"
UNSUITABLE_STATUSES = {
    "請/採購人員認為不適合進行(數位內容採購)",
    "請/採購人員認為不適合進行",
}


def _audit_notes(row: ContractRow) -> str:
    notes: list[str] = []
    status = resolve_status(row.contract_status_raw)
    if status == WAITING_STATUS:
        notes.append(WAITING_STATUS)
    if resolve_department(row.requester_unit) == "未分類(單位)":
        notes.append("未分類(單位)")
    if status in UNSUITABLE_STATUSES:
        notes.append("不適合進行")
    return ";".join(notes)


def render_exception_report(workbook: Workbook, rows: list[ContractRow], now: datetime | None = None) -> None:
    ws = workbook.create_sheet("稽核異常清單")
    ws.append([
        "契約編號",
        "契約名稱",
        "契約金額",
        "[統編]供應商名稱",
        "請購人單位",
        "請購人",
        "契約狀態",
        "稽核註記",
    ])
    apply_header_style(ws)

    for row in rows:
        notes = _audit_notes(row)
        if not notes:
            continue
        ws.append(
            [
                row.contract_id,
                row.contract_name,
                row.contract_amount,
                row.vendor_name_raw,
                row.requester_unit,
                row.requester_name,
                resolve_status(row.contract_status_raw),
                notes,
            ]
        )

    content_end_row = ws.max_row
    apply_body_borders(ws, start_row=1, end_row=content_end_row)
    append_stat_date(ws, now=now)
    apply_standard_layout(ws, "A2")
    auto_fit_columns(ws, max_row=content_end_row)
