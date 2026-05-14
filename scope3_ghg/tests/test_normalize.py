from scope3_ghg.normalize import normalize_compact_text, to_safe_number


def test_normalize_compact_text_removes_spaces() -> None:
    assert normalize_compact_text("  A\u3000B  ") == "AB"


def test_to_safe_number_defaults_zero() -> None:
    assert to_safe_number("bad") == 0.0
