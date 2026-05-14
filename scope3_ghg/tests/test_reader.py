import pytest

from scope3_ghg.reader import SourceReadError, _build_header_index


def test_build_header_index_required_ok() -> None:
    columns = [
        "契約編號",
        "契約名稱",
        "契約金額",
        "請購人單位",
        "請購人",
        "契約狀態",
        "KPI",
        "[統編]供應商名稱",
        "供應商是否簽署淨零承諾",
    ]
    idx = _build_header_index(columns)
    assert idx["contract_id"] == 0


def test_build_header_index_missing_required() -> None:
    with pytest.raises(SourceReadError):
        _build_header_index(["契約編號"])
