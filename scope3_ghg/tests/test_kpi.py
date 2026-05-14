from scope3_ghg.kpi import compute_performance
from scope3_ghg.models import ContractRow


def build_row(
    contract_id: str,
    vendor_name_raw: str,
    net_zero_commitment_raw: str,
    contract_amount: float = 30_000_000,
) -> ContractRow:
    return ContractRow(
        contract_id=contract_id,
        contract_name=f"contract-{contract_id}",
        contract_amount=contract_amount,
        requester_unit="政府應用處",
        requester_name="tester",
        contract_status_raw="資料通過顧問審核標準",
        kpi_key="盤查範圍契約",
        vendor_name_raw=vendor_name_raw,
        net_zero_commitment_raw=net_zero_commitment_raw,
        iso14064_evidence_raw="",
    )


def test_compute_performance_kpi_b_deduplicates_unsigned_vendors() -> None:
    rows = [
        build_row("A-001", "供應商甲", "未簽署"),
        build_row("A-002", "供應商甲", "未簽署"),
        build_row("B-001", "供應商乙", "已簽署"),
        build_row("C-001", "供應商丙", "已簽署"),
    ]

    perf = compute_performance(rows)

    assert perf.kpiB_ratio == 0.67
    assert perf.scoreB == 3.33


def test_compute_performance_kpi_b_uses_kpi_key_only() -> None:
    rows = [
        ContractRow(
            contract_id="KPI-001",
            contract_name="kpi-base-self-review",
            contract_amount=30_000_000,
            requester_unit="政府應用處",
            requester_name="tester",
            contract_status_raw="自主盤查契約審核中",
            kpi_key="盤查範圍契約",
            vendor_name_raw="供應商甲",
            net_zero_commitment_raw="未簽署",
            iso14064_evidence_raw="",
        ),
        ContractRow(
            contract_id="KPI-002",
            contract_name="kpi-base-approved",
            contract_amount=30_000_000,
            requester_unit="政府應用處",
            requester_name="tester",
            contract_status_raw="資料通過顧問審核標準",
            kpi_key="盤查範圍契約",
            vendor_name_raw="供應商乙",
            net_zero_commitment_raw="已簽署",
            iso14064_evidence_raw="",
        ),
        ContractRow(
            contract_id="KPI-003",
            contract_name="non-kpi-self-review",
            contract_amount=30_000_000,
            requester_unit="政府應用處",
            requester_name="tester",
            contract_status_raw="自主盤查契約審核中",
            kpi_key="其他KPI",
            vendor_name_raw="供應商丙",
            net_zero_commitment_raw="未簽署",
            iso14064_evidence_raw="",
        ),
    ]

    perf = compute_performance(rows)

    # KPI_B 僅以 KPI=盤查範圍契約 的供應商母體計算。
    # 供應商甲（未簽）與供應商乙（已簽）納入；供應商丙（非 KPI_BASE_KEY）排除。
    assert perf.kpiB_ratio == 0.5
    assert perf.scoreB == 2.5