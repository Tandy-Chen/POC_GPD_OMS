# 供應鏈碳管理專案（Scope 3）

## Python 化系統設計與欄位規格 v0.1

本文件將既有 ExcelScript 報表流程轉為 Python 專案規格，作為後續開發與驗收基準。

## 1. 專案目標與範圍

- 目標：以 Python 重建既有 Scope 3 報表流程，取代 PA + Script 組合。
- 輸出維持既有制度：
  - 統計分析_矩陣
  - 稽核異常清單
  - 碳盤查績效統計
  - 碳盤查績效統計_各部門分表（含未分類）
- 輸出檔附加來源資料快照：
  - 來源檔對應 sheet（預設 sheet1）完整複製為結果檔內獨立 sheet，作為事後驗證與稽核證據。
- 統計口徑與 KPI 治理遵循目前腳本版本 v2.7.0。

## 2. 建議 Python 專案架構

```text
scope3_ghg/
  pyproject.toml
  README.md
  src/scope3_ghg/
    __init__.py
    config.py               # 常數、開關、欄位 alias、部門映射
    models.py               # 資料模型(dataclass / pydantic)
    normalize.py            # 字串正規化、欄位清理工具
    reader.py               # 來源資料讀取與欄位驗證
    aggregators.py          # 部門聚合、unique 供應商計算
    kpi.py                  # KPI 與績效分數計算
    reports/
      matrix_report.py      # 統計分析_矩陣
      exception_report.py   # 稽核異常清單
      performance_report.py # 碳盤查績效統計 + 分表
      style.py              # 欄寬、樣式、統計日期列
    pipeline.py             # 單一流程入口
    cli.py                  # 命令列進入點
  tests/
    test_normalize.py
    test_mapping.py
    test_kpi.py
    test_reports.py
```

## 3. 輸入資料契約

### 3.1 來源工作表

- 預設來源 sheet：sheet1

### 3.2 必要欄位（邏輯欄位）

- contractId
- contractName
- contractAmount
- requesterUnit
- requesterName
- contractStatusRaw
- kpiKey
- vendorNameRaw
- netZeroCommitmentRaw

### 3.3 可選欄位

- iso14064EvidenceRaw

### 3.4 欄位別名（alias）

- contractId: 契約編號
- contractName: 契約名稱
- contractAmount: 契約金額
- requesterUnit: 請購人單位
- requesterName: 請購人
- contractStatusRaw: 契約狀態
- kpiKey: KPI
- vendorNameRaw: [統編]供應商名稱
- netZeroCommitmentRaw: 供應商是否簽署淨零承諾
- iso14064EvidenceRaw:
  - ISO14064證書輔導實績
  - 供應商是否取得 ISO 14064-1 有效查證聲明

### 3.5 欄位驗證規則

- 必要欄位缺失即中止流程並回報錯誤清單。
- contractAmount 轉為數值失敗時視為 0。
- 文字欄位均進行不可見空白與前後空白清理。

## 4. 主資料模型

```python
ContractRow
- contract_id: str
- contract_name: str
- contract_amount: float
- requester_unit: str
- requester_name: str
- contract_status_raw: str
- kpi_key: str
- vendor_name_raw: str
- net_zero_commitment_raw: str
- iso14064_evidence_raw: str
```

## 5. 制度常數與映射

### 5.1 部門順序（輸出欄位固定）

- 政府處
- 智聯處
- 雲端處
- 系統處
- 營發處
- 中資處
- 商應處
- 企應處
- 行政處
- 未分類(單位)

### 5.2 契約狀態 7 類

- 等待供應商上傳第一筆資料
- 供應商已上傳資料，等待顧問審核
- 供應商已上傳增補資料，等待顧問審核
- 顧問表示有待解決事項，等待供應商上傳
- 資料通過顧問審核標準
- 請/採購人員認為不適合進行(數位內容採購)
- 請/採購人員認為不適合進行

### 5.3 KPI 治理

- KPI_BASE_KEY = 盤查範圍契約
- A3_ASSUME_IN_REPORT_IS_COMPLIANT = true（目前口徑）

## 6. 統計與聚合規格

### 6.1 部門解析

- 以請購人單位關鍵字比對部門。
- 多命中時取關鍵字較長者。
- 無法命中時標記未分類(單位)。

### 6.2 狀態解析

- 契約狀態文字包含上述 7 類之一即歸類。
- 未命中時標記其他。

### 6.3 聚合函式

- aggregate_by_dept(rows, predicate, exclude_unsuitable)
  - 輸出每部門件數、全集件數、全集金額(百萬元)
  - 全集含未分類(單位)，部門欄位亦含未分類(單位)

### 6.4 不重複供應商

- 僅計 KPI_BASE_KEY 母體。
- 供應商鍵值去除不可見空白與一般空白。
- 部門欄位為各部門 unique，契約總計為全域 unique（不可直接加總部門）。

## 7. 報表規格

### 7.1 統計分析_矩陣

- 表頭：管控項目 + 10 部門(含未分類(單位)) + 契約總計 + 金額總計(百萬元)
- 列定義：
  - 已簽3000萬元(含)以上列管契約案
  - 狀態 7 類
  - 自主盤查契約
  - 盤查範圍契約(持續盤查契約)
  - 資分碳智雲上載契約案
  - 不重複供應商數
  - 未簽署淨零承諾契約案
- 附加檢核區塊：
  - 檢核（依契約狀態合計）
  - 檢核（部門金額合計，百萬元）
  - 含未落入部門統計件數/金額
- 附註列：統計口徑說明。

### 7.2 稽核異常清單

- 欄位：契約編號、契約名稱、契約金額、[統編]供應商名稱、請購人單位、請購人、契約狀態、稽核註記
- 納入條件：
  - 等待供應商上傳第一筆資料
  - 未分類(單位)
  - 兩類不適合進行
- 稽核註記可同時包含多標籤（以分號串接）。

### 7.3 碳盤查績效統計（總表 + 分表）

- 主表：碳盤查績效統計（資分）
- 分表：碳盤查績效統計_部門名（9 部門 + 未分類(單位)）
- 指標：
  - A1 盤查件數達成率
  - A2 盤查契約金額達成率
  - A3 碳足跡條款落實達成率
  - B 供應商淨零承諾達成率
  - C ISO 14064-1 輔導證書達成率
- B 指標口徑：
  - 分母：KPI_BASE_KEY 母體中的不重複供應商總數
  - 分子：上述不重複供應商總數，扣除其中「未簽署淨零承諾」的不重複供應商數
  - 納入條件僅看 KPI 欄位是否為「盤查範圍契約」，且母體單位為「不重複供應商」；不得以契約狀態（包含「自主盤查契約審核中」）作為 B 指標額外納入或排除條件
- 分數：
  - A1: a1 * 50
  - A2: a2 * 40
  - A3: a3 * 10
  - B: b * 5
  - C: c * 5
  - total_raw = A + B + C
  - total_calc = max(10 * sqrt(A_sum) + B + C, 70)

## 8. 樣式與輸出行為

- 報表樣式可選套用 TableStyleMedium2。
- 欄寬自動調整，最小欄寬 12。
- 主體資料區套用儲存格邊框與格線（含各主要工作表與來源快照 sheet）。
- 績效表 A/B/C 欄最小寬度 34/14/16。
- 表頭字色 #003399。
- 各工作表凍結表頭列（依表型設定凍結列）。
- 附註與統計日期採跨欄顯示，且不納入欄寬估算。
- 所有主表與分表末列附上統計日期（台北時區 UTC+8）。

## 9. 錯誤處理與可觀測性

- 必要欄位缺失：拋出可讀錯誤，附 alias 清單。
- 輸入檔讀取失敗：區分格式錯誤、路徑錯誤、權限錯誤、來源檔未定位。
- 產生執行摘要：
  - 來源檔路徑（自動定位結果）
  - 來源列數
  - 有效列數
  - 未分類件數
  - 異常清單件數
  - 輸出檔路徑

## 10. 版本策略與驗收建議

### 10.1 版本切分

- v0.1 規格確認（本文件）
- v0.2 Python 骨架與資料讀取
- v0.3 報表與 KPI 完整輸出
- v1.0 與現行報表比對驗收

### 10.2 驗收基準

- 同一份來源資料，Python 版與現行 Script 版在下列面向一致：
  - 各矩陣列之部門件數與總計
  - 稽核異常清單件數與標記
  - A1/A2/A3/B/C 與總分
  - 各分表數值

### 10.3 檔案管理驗收

- 來源檔自動定位（條件匹配）成功
- 輸出檔寫入指定目錄，日期時戳無重複

## 11. 決策點確認

### 11.1 已確認決策

- A3 採「入報表即合規」口徑 ✅
- HQ_DESIGNATED_SUPPLIER_COUNT = 1 ✅
- 稽核註記字詞沿用現行版本 ✅
- 保留 Excel 樣式格式化 ✅

## 12. 檔案目錄策略

### 12.1 來源檔管理

- 位置：專案外之專用目錄（例如 `inputs/`）
- 識別規則：副檔名 `.xlsx` 且檔名包含 `範疇三業務管理報表`
- 優點：來源檔日期變化時自動適配，無需修改配置

### 12.2 輸出檔管理

- 位置：專案外之專用目錄（例如 `outputs/`）
- 格式：Excel 檔案（.xlsx），含日期時戳避免重名
- 命名樣板：`SCOPE3_Report_GE{民國年}_各單位績效_YYYYMMDD_HHMM.xlsx`
- 年碼規則：取當年度民國年，例如 2026 年為 `GE115`，2027 年為 `GE116`
- 參考樣式：`SCOPE3_Report_GE115_各單位績效_20260511_0843.xlsx`
- 包含檔案：
  - 統計分析_矩陣
  - 稽核異常清單
  - 碳盤查績效統計 + 各部門分表（多個 sheet）
  - 來源資料快照 sheet（預設命名：來源資料_sheet1）
  - 口徑要項彙總（置於結果檔最後）
