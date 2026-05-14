"""KPI computation module."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .aggregators import resolve_status
from .config import A3_ASSUME_IN_REPORT_IS_COMPLIANT, KPI_BASE_KEY
from .models import ContractRow
from .normalize import normalize_compact_text

HQ_DESIGNATED_SUPPLIER_COUNT = 1
APPROVED_STATUS = "資料通過顧問審核標準"
UNSUITABLE_DIGITAL_STATUS = "請/採購人員認為不適合進行(數位內容採購)"
UNSUITABLE_STATUSES = {
    UNSUITABLE_DIGITAL_STATUS,
    "請/採購人員認為不適合進行",
}


def round_to_2(value: float) -> float:
    return round(value + 1e-12, 2)


def safe_divide(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def clamp_ratio(value: float) -> float:
    return max(0.0, min(value, 1.0))


def normalize_vendor_key(value: str) -> str:
    return normalize_compact_text(value).replace(" ", "")


@dataclass(slots=True)
class PerformanceResult:
    kpiA1_pct: float
    kpiA2_pct: float
    kpiA3_pct: float
    kpiB_ratio: float
    kpiC_ratio: float
    scoreA1: float
    scoreA2: float
    scoreA3: float
    scoreB: float
    scoreC: float
    total_calc: float
    total_raw: float


def compute_performance(rows: list[ContractRow]) -> PerformanceResult:
    signed_over_30m = [row for row in rows if row.contract_amount >= 30_000_000]
    signed_count = len(signed_over_30m)
    signed_amount_m = round_to_2(sum(row.contract_amount for row in signed_over_30m) / 1_000_000)

    approved = [row for row in signed_over_30m if resolve_status(row.contract_status_raw) == APPROVED_STATUS]
    approved_count = len(approved)
    approved_amount_m = round_to_2(sum(row.contract_amount for row in approved) / 1_000_000)

    unsuitable_digital_count = sum(
        1 for row in signed_over_30m if resolve_status(row.contract_status_raw) == UNSUITABLE_DIGITAL_STATUS
    )
    eligible_a3_count = sum(
        1 for row in signed_over_30m if resolve_status(row.contract_status_raw) not in UNSUITABLE_STATUSES
    )
    carbon_upload_count_old = sum(
        1
        for row in signed_over_30m
        if normalize_compact_text(row.kpi_key) == KPI_BASE_KEY and resolve_status(row.contract_status_raw) not in UNSUITABLE_STATUSES
    )
    carbon_upload_count = eligible_a3_count if A3_ASSUME_IN_REPORT_IS_COMPLIANT else carbon_upload_count_old

    global_vendor_set: set[str] = set()
    for row in rows:
        if normalize_compact_text(row.kpi_key) != KPI_BASE_KEY:
            continue
        vendor_key = normalize_vendor_key(row.vendor_name_raw)
        if vendor_key:
            global_vendor_set.add(vendor_key)
    unique_vendor_total = len(global_vendor_set)

    net_zero_not_signed_vendor_set: set[str] = set()
    for row in rows:
        if normalize_compact_text(row.kpi_key) != KPI_BASE_KEY:
            continue
        if "未簽" not in normalize_compact_text(row.net_zero_commitment_raw):
            continue
        vendor_key = normalize_vendor_key(row.vendor_name_raw)
        if vendor_key:
            net_zero_not_signed_vendor_set.add(vendor_key)
    net_zero_not_signed_vendor_count = len(net_zero_not_signed_vendor_set)

    a1 = clamp_ratio(safe_divide(approved_count, signed_count * 0.83))
    a2 = clamp_ratio(safe_divide(approved_amount_m, signed_amount_m * 0.83))
    a3 = clamp_ratio(safe_divide(carbon_upload_count, signed_count - unsuitable_digital_count))
    b = clamp_ratio(safe_divide(unique_vendor_total - net_zero_not_signed_vendor_count, unique_vendor_total))

    iso_certified_vendor_set: set[str] = set()
    for row in rows:
        if normalize_compact_text(row.kpi_key) != KPI_BASE_KEY:
            continue
        vendor_key = normalize_vendor_key(row.vendor_name_raw)
        if not vendor_key:
            continue
        flag = normalize_compact_text(row.iso14064_evidence_raw)
        if flag and "無資料" not in flag and "未" not in flag and "否" not in flag:
            iso_certified_vendor_set.add(vendor_key)

    iso_certified_vendor_count = len(iso_certified_vendor_set)
    c = clamp_ratio(
        safe_divide(min(iso_certified_vendor_count, HQ_DESIGNATED_SUPPLIER_COUNT), HQ_DESIGNATED_SUPPLIER_COUNT)
    )

    kpiA1_pct = round_to_2(a1 * 100)
    kpiA2_pct = round_to_2(a2 * 100)
    kpiA3_pct = round_to_2(a3 * 100)
    kpiB_ratio = round_to_2(b)
    kpiC_ratio = round_to_2(c)

    scoreA1 = round_to_2(a1 * 50)
    scoreA2 = round_to_2(a2 * 40)
    scoreA3 = round_to_2(a3 * 10)
    scoreB = round_to_2(b * 5)
    scoreC = round_to_2(c * 5)

    sum_a = scoreA1 + scoreA2 + scoreA3
    total_raw = round_to_2(sum_a + scoreB + scoreC)
    total_calc = round_to_2(max(10 * sqrt(sum_a) + scoreB + scoreC, 70))

    return PerformanceResult(
        kpiA1_pct=kpiA1_pct,
        kpiA2_pct=kpiA2_pct,
        kpiA3_pct=kpiA3_pct,
        kpiB_ratio=kpiB_ratio,
        kpiC_ratio=kpiC_ratio,
        scoreA1=scoreA1,
        scoreA2=scoreA2,
        scoreA3=scoreA3,
        scoreB=scoreB,
        scoreC=scoreC,
        total_calc=total_calc,
        total_raw=total_raw,
    )
