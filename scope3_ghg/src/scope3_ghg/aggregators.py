"""Aggregation helpers."""

from __future__ import annotations

from collections import Counter

from .config import CONTRACT_STATUS_7, DEPT_KEYWORDS, DEPT_ORDER
from .models import ContractRow
from .normalize import normalize_compact_text

UNCLASSIFIED_DEPT = "未分類(單位)"
OTHER_STATUS = "其他"


def resolve_department(requester_unit: str) -> str:
    normalized = normalize_compact_text(requester_unit)
    hits: list[tuple[str, str]] = []
    for dept, keywords in DEPT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                hits.append((dept, keyword))

    if hits:
        return max(hits, key=lambda item: len(item[1]))[0]

    for dept, keywords in DEPT_KEYWORDS.items():
        for keyword in keywords:
            compact_keyword = keyword.replace("處", "")
            if compact_keyword and compact_keyword in normalized:
                return dept

    return UNCLASSIFIED_DEPT


def resolve_status(contract_status_raw: str) -> str:
    normalized = normalize_compact_text(contract_status_raw)
    for status in CONTRACT_STATUS_7:
        if status in normalized:
            return status
    return OTHER_STATUS


def group_rows_by_department(rows: list[ContractRow]) -> dict[str, list[ContractRow]]:
    grouped: dict[str, list[ContractRow]] = {dept: [] for dept in DEPT_ORDER}
    for row in rows:
        grouped.setdefault(resolve_department(row.requester_unit), []).append(row)
    return grouped


def aggregate_by_dept(rows: list[ContractRow], predicate, exclude_unsuitable: bool) -> tuple[list[int], int, float]:
    unsuitable_statuses = {
        "請/採購人員認為不適合進行(數位內容採購)",
        "請/採購人員認為不適合進行",
    }
    filtered_rows = [
        row
        for row in rows
        if predicate(row) and not (exclude_unsuitable and resolve_status(row.contract_status_raw) in unsuitable_statuses)
    ]

    dept_counts = [0 for _ in DEPT_ORDER]
    for row in filtered_rows:
        dept = resolve_department(row.requester_unit)
        dept_counts[DEPT_ORDER.index(dept)] += 1

    total_amount_million = round(sum(row.contract_amount for row in filtered_rows) / 1_000_000, 2)
    return dept_counts, len(filtered_rows), total_amount_million


def compute_unique_vendor_counts_for_carbon_kpi(rows: list[ContractRow], kpi_base_key: str) -> tuple[list[int], int]:
    dept_vendor_sets = {dept: set() for dept in DEPT_ORDER}
    all_vendors: set[str] = set()

    for row in rows:
        if normalize_compact_text(row.kpi_key) != kpi_base_key:
            continue
        vendor_key = normalize_compact_text(row.vendor_name_raw).replace(" ", "")
        if not vendor_key:
            continue
        dept = resolve_department(row.requester_unit)
        dept_vendor_sets[dept].add(vendor_key)
        all_vendors.add(vendor_key)

    return [len(dept_vendor_sets[dept]) for dept in DEPT_ORDER], len(all_vendors)


def count_by_requester_unit(rows: list[ContractRow]) -> dict[str, int]:
    counter: Counter[str] = Counter(resolve_department(r.requester_unit) for r in rows)
    return dict(counter)
