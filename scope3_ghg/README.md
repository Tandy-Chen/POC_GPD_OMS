# scope3_ghg (v0.3)

供應鏈碳盤查報表自動化工具。支援 Windows 快速啟動、命令列操作，以及完整的來源資料稽核。

## 功能特色

- ✅ 供應商淨零承諾達成率（KPI-B）計算穩定化
- ✅ 來源檔自動搜尋與驗證
- ✅ CLI `validate` / `process` 兩種操作模式
- ✅ 多維度績效報表（矩陣、異常清單、各部門績效）
- ✅ 結果檔內附來源資料快照，便於事後稽核
- ✅ Windows 啟動檔 `scope3-ghg.cmd` / `scope3-ghg.ps1`

## 常態操作流程

### 第 1 步：準備來源檔

1. 取得業務系統的「範疇三業務管理報表」Excel 檔
2. 將檔案複製到 `scope3_ghg/inputs/` 目錄
3. 檔名自動搜尋條件：`.xlsx` 且包含「範疇三業務管理報表」

### 第 2 步：執行報表生成

**方式 A：直接執行（推薦）**

```powershell
cd "C:\Tandy資料夾\APPdata\supply-chain-carbon-management"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\scope3-ghg.ps1 process
```

預設行為：
- 自動尋找 `scope3_ghg/inputs/` 內的來源檔
- 使用 `sheet1`
- 生成完整報表到 `scope3_ghg/outputs/`
- 檔名格式：`SCOPE3_Report_GE{民國年}_各單位績效_{YYYYMMDD}_{HHMM}.xlsx`

**方式 B：PowerShell（便於指定參數）**

```powershell
.\scope3-ghg.ps1 process `
  --SourcePath "C:\path\to\your\file.xlsx" `
  --Sheet sheet1 `
  --OutputDir "C:\custom\output\path"
```

**方式 C：命令列直接調用**

```bash
python -m scope3_ghg.cli process --sheet sheet1
```


### 第 3 步：取得輸出報表

完成後，報表會生成在 `scope3_ghg/outputs/` 目錄，檔名含時間戳便於區分版本。

## 驗證來源檔（不生成報表）

如果只想驗證來源檔格式與內容，使用 `validate` 模式：

```powershell
.\scope3-ghg.ps1 validate --Sheet sheet1
```

或直接調用 CLI：

```bash
python -m scope3_ghg.cli validate --sheet sheet1
```

## 輸出報表說明

### 報表內容

生成的 Excel 檔包含以下 Sheets：

| 名稱 | 說明 |
|------|------|
| `統計分析_矩陣` | 各部門簽約件數與金額統計 |
| `稽核異常清單` | 未符合要求的契約列表 |
| `碳盤查績效統計（*部門）` | 各部門 KPI 分數（A1/A2/A3/B/C） |
| `來源資料_sheet1` | 原始來源檔內容快照 |
| `口徑要項彙總` | KPI 計算參數與中間值（用於稽核） |

### 檔名規則

- 前綴：`SCOPE3_Report_GE{民國年}_各單位績效`
- 完整例：`SCOPE3_Report_GE115_各單位績效_20260514_1505.xlsx`
- 民國年自動推導，2026 年 = 民國 115
- 時間戳確保同日多次執行不會覆蓋舊結果

## 目錄結構

```
supply-chain-carbon-management/
├── scope3-ghg.cmd             (Windows 啟動批檔)
├── scope3-ghg.ps1             (PowerShell 啟動腳本)
├── pyproject.toml             (專案配置)
├── requirements-offline.txt   (依賴清單)
├── README.md                  (本檔案)
└── scope3_ghg/
    ├── src/
    │   └── scope3_ghg/
    │       ├── cli.py              (命令列介面)
    │       ├── pipeline.py         (報表生成核心邏輯)
    │       ├── kpi.py              (KPI 計算模組)
    │       ├── reader.py           (來源檔讀取)
    │       ├── config.py           (配置常數)
    │       └── reports/            (報表格式與樣式)
    ├── tests/                      (單元測試)
    ├── inputs/                     (📂 放置來源檔)
    └── outputs/                    (📂 報表輸出目錄)
```

## 已知限制與注意事項

### 格式要求
- 來源檔必須是 `.xlsx`（Microsoft Excel 2007+ 格式）
- 檔案不能被密碼保護或加密
- 必須包含特定欄位（詳見來源快照 Sheet）

### 計算基準
- **KPI-B（供應商淨零承諾達成率）**：
  - 只計算簽約額 ≥ NT$3,000 萬的契約
  - 母數 = 不重複供應商總數（該維度）
  - 分子 = 母數 - 未簽署淨零承諾的不重複供應商數
  - 修復版本（v0.3）已統一維度，確保計算穩定

### 自動搜尋條件
- 副檔名：`.xlsx`
- 檔名必須含：`範疇三業務管理報表`
- 若符合條件的檔案超過 1 個，系統會報錯並要求明確指定

## 測試與驗證

### 執行測試套件

```bash
cd scope3_ghg
pytest -v
```

### 回歸測試清單

- ✅ KPI-B 維度一致性：用相同來源檔執行 2 次，確認 KPI-B 結果完全相同
- ✅ 供應商去重邏輯：驗證 `global_vendor_set` 無重複
- ✅ 未簽署偵測：檢查「未簽」文字正規化與判定
- ✅ 報表生成：確認所有 Sheets 都被建立且內容非空

## 常見問題

### Q: 來源檔放進 `inputs/` 後執行報錯
- A: 檢查檔名是否包含「範疇三業務管理報表」，以及檔案格式是否為 `.xlsx`

### Q: 多執行幾次為何 KPI-B 都相同
- A: 這是正確行為！v0.3 已修復維度混用，現在結果應該穩定。若看到不同，請檢查來源檔是否真的相同。

### Q: 如何指定只處理某個工作表
- A: 使用 `--Sheet` 參數，例如 `.\scope3-ghg.ps1 process --Sheet sheet2`

---

**版本紀錄**

| 版本 | 日期 | 主要改動 |
|------|------|--------|
| v0.3 | 2026-05-14 | 統一 KPI-B 供應商母數維度，修復計算波動 |
| v0.2 | 2026-05-13 | Windows 啟動檔、多維度報表、來源快照 |
| v0.1 | 2026-05-12 | CLI 基礎功能 |
