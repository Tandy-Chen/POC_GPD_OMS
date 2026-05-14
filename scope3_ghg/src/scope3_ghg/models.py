"""Domain models."""

from dataclasses import dataclass


@dataclass(slots=True)
class ContractRow:
    contract_id: str
    contract_name: str
    contract_amount: float
    requester_unit: str
    requester_name: str
    contract_status_raw: str
    kpi_key: str
    vendor_name_raw: str
    net_zero_commitment_raw: str
    iso14064_evidence_raw: str
