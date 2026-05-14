from scope3_ghg.aggregators import UNCLASSIFIED_DEPT, resolve_department


def test_resolve_department_matches_script_aliases() -> None:
    assert resolve_department("政府應用處維運科") == "政府處"
    assert resolve_department("智慧聯網處測試小組") == "智聯處"
    assert resolve_department("營運系統管理處") == "系統處"
    assert resolve_department("行政管理處") == "行政處"


def test_resolve_department_supports_compact_keyword_fallback() -> None:
    assert resolve_department("政府應用部門") == "政府處"
    assert resolve_department("企業應用發展部") == "企應處"


def test_resolve_department_falls_back_to_unclassified() -> None:
    assert resolve_department("完全未知單位") == UNCLASSIFIED_DEPT