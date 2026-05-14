# scope3_ghg (v0.2)

這個版本已補上 Windows 可直接執行的啟動檔，並保留現有 CLI 介面。

## 已具備功能

- Source file 自動搜尋與驗證
- CLI `validate` / `process`
- 報表輸出至 `outputs/`
- 結果檔附加來源資料快照 sheet
- Windows 啟動檔 `scope3-ghg.cmd` / `scope3-ghg.ps1`

## Windows 快速使用

### 方式 1：雙擊執行

直接執行專案根目錄的 `scope3-ghg.cmd`，它會自動切換到 `scope3_ghg/` 子專案再執行。

預設行為：

- 自動尋找 `scope3_ghg/inputs/` 內符合條件的 `.xlsx`
- 使用 `sheet1`
- 執行 `process`
- 輸出到 `scope3_ghg/outputs/`

### 方式 2：PowerShell 執行

```powershell
Set-Location "C:\Tandy資料夾\APPdata\supply-chain-carbon-management"
.\scope3-ghg.ps1
```

### 方式 3：直接呼叫 CLI

```bash
python -m pip install -e .
scope3-ghg process --sheet sheet1
```

### 驗證來源檔

```bash
scope3-ghg validate --sheet sheet1
```

### 指定來源檔

```bash
scope3-ghg process --input "path/to/your/file.xlsx" --sheet sheet1
```

## 目錄結構

```text
my_workspace/
  supply-chain-carbon-management/
    scope3-ghg.cmd     (根目錄雙擊啟動)
    scope3-ghg.ps1     (根目錄 PowerShell 啟動)
    scope3_ghg/
      src/
      inputs/          (來源資料)
      outputs/         (生成報表)
```

## 輸出檔規則

- 檔名前綴：`SCOPE3_Report_GE{民國年}_各單位績效`
- 檔名格式：`SCOPE3_Report_GE115_各單位績效_20260511_0843.xlsx`
- GE 年碼會依執行年度動態推導，不會寫死
- 結果檔會附加來源資料快照 sheet，預設名稱為 `來源資料_sheet1`

## 注意事項

- 檔案需可被 Python 讀取，不能是加密 Office 容器
- 自動搜尋條件：副檔名 `.xlsx` 且檔名含 `範疇三業務管理報表`
- 若使用本機虛擬環境，launcher 會優先尋找專案根目錄或上一層工作區的 `.venv`
