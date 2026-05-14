"""Summary report renderer for key governance points."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook

from .style import append_stat_date, apply_body_borders, apply_header_style, apply_standard_layout, auto_fit_columns

SHEET_NAME = "口徑要項彙總"


def render_summary_report(
    workbook: Workbook,
    source_path: Path | None = None,
    source_rows: int | None = None,
    now: datetime | None = None,
) -> None:
    ws = workbook.create_sheet(SHEET_NAME)
    ws.append(["主題", "要項彙總", "來源"])
    apply_header_style(ws, 1)

    rows = [
        ["KPI_B 母體", "僅納入 KPI 欄為『盤查範圍契約』之資料，且以不重複供應商為單位計算。", "Script + 規格"],
        ["KPI_B 分子分母量綱", "分母為不重複供應商總數；分子為分母扣除未簽署淨零承諾之不重複供應商數。", "Script 修正"],
        ["契約狀態與 KPI_B", "不得以契約狀態（含『自主盤查契約審核中』）作為 KPI_B 額外納入或排除條件。", "規格"],
        ["A3 治理口徑", "A3 依目前制度採『入報表即合規』。", "規格"],
        ["部門映射", "請購單位需先做 alias 對映；無法命中時歸『未分類(單位)』。", "Script + 規格"],
        ["稽核異常納入", "異常清單納入等待上傳第一筆、未分類、兩類不適合進行。", "Script + 規格"],
        ["追溯證據", "結果檔附加來源資料快照 sheet（預設來源資料_sheet1），供事後重算比對。", "實作"],
        ["可讀性", "主體資料區套用表格邊框、凍結表頭；註記與統計日期採跨欄顯示且不影響欄寬。", "實作"],
    ]
    if source_path is not None:
        rows.insert(0, ["本次來源檔案", source_path.name, "本次執行"])
    if source_rows is not None:
        rows.insert(1 if source_path is not None else 0, ["本次來源列數", source_rows, "本次執行"])

    for row in rows:
        ws.append(row)

    content_end_row = ws.max_row
    apply_body_borders(ws, start_row=1, end_row=content_end_row)
    append_stat_date(ws, now=now)
    apply_standard_layout(ws, "A2")
    auto_fit_columns(ws, explicit_widths={"A": 18, "B": 72, "C": 14}, max_row=content_end_row)
