"""Configuration and governance constants."""

from datetime import datetime
from pathlib import Path

MINGUO_YEAR_OFFSET = 1911
SCRIPT_NAME_PREFIX = "SCOPE3_GHG_Report"
OUTPUT_REPORT_PREFIX = "SCOPE3_Report"
OUTPUT_REPORT_SUFFIX = "各單位績效"


def get_report_year_code(now: datetime | None = None) -> str:
    current_year = (now or datetime.now()).year
    return f"GE{current_year - MINGUO_YEAR_OFFSET}"


def build_script_id(now: datetime | None = None) -> str:
    return f"{SCRIPT_NAME_PREFIX}_{get_report_year_code(now)}"


def build_output_file_prefix(now: datetime | None = None) -> str:
    return f"{OUTPUT_REPORT_PREFIX}_{get_report_year_code(now)}_{OUTPUT_REPORT_SUFFIX}"


SCRIPT_ID = build_script_id()
SCRIPT_VERSION = "v2.7.0"
DEFAULT_SOURCE_SHEET = "sheet1"

# Directory management
DEFAULT_INPUT_DIR = Path("inputs")
DEFAULT_OUTPUT_DIR = Path("outputs")
OUTPUT_FILE_EXTENSION = "xlsx"

# Source file identification
SOURCE_FILE_PATTERN_EXT = "xlsx"
SOURCE_FILE_PATTERN_NAME = "範疇三業務管理報表"

DEPT_ORDER = [
    "政府處",
    "智聯處",
    "雲端處",
    "系統處",
    "營發處",
    "中資處",
    "商應處",
    "企應處",
    "行政處",
    "未分類(單位)",
]

DEPT_KEYWORDS = {
    "政府處": ["政府應用處"],
    "智聯處": ["智慧聯網處"],
    "雲端處": ["雲端系統處"],
    "系統處": ["營運系統管理處"],
    "營發處": ["營運系統發展處"],
    "中資處": ["中部資訊應用處"],
    "商應處": ["商務應用處"],
    "企應處": ["企業應用發展處"],
    "行政處": ["行政管理處"],
}

CONTRACT_STATUS_7 = [
    "等待供應商上傳第一筆資料",
    "供應商已上傳資料，等待顧問審核",
    "供應商已上傳增補資料，等待顧問審核",
    "顧問表示有待解決事項，等待供應商上傳",
    "資料通過顧問審核標準",
    "請/採購人員認為不適合進行(數位內容採購)",
    "請/採購人員認為不適合進行",
]

KPI_BASE_KEY = "盤查範圍契約"
A3_ASSUME_IN_REPORT_IS_COMPLIANT = True

SOURCE_COLUMN_ALIASES = {
    "contract_id": ["契約編號"],
    "contract_name": ["契約名稱"],
    "contract_amount": ["契約金額"],
    "requester_unit": ["請購人單位"],
    "requester_name": ["請購人"],
    "contract_status_raw": ["契約狀態"],
    "kpi_key": ["KPI"],
    "vendor_name_raw": ["[統編]供應商名稱"],
    "net_zero_commitment_raw": ["供應商是否簽署淨零承諾"],
    "iso14064_evidence_raw": [
        "ISO14064證書輔導實績",
        "供應商是否取得 ISO 14064-1 有效查證聲明",
    ],
}

REQUIRED_FIELDS = [
    "contract_id",
    "contract_name",
    "contract_amount",
    "requester_unit",
    "requester_name",
    "contract_status_raw",
    "kpi_key",
    "vendor_name_raw",
    "net_zero_commitment_raw",
]
