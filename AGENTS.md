# Repository Guidelines

## 專案概觀 (Project Overview)
TimeScheduler 是一個輕量級、基於記憶體 (memory-based) 的 Python 任務排程套件。它提供簡單的 API 來管理定時與背景任務，無需依賴外部資料庫。

### 核心技術 (Core Technologies)
- **語言：** Python (>= 3.13)
- **並行處理 (Concurrency)：** 多執行緒 (Multi-threading，使用 `threading` 模組)
- **建置系統：** `uv` (搭配 `pyproject.toml` 與 `uv.lock`)
- **測試框架：** `pytest` (內部使用 `unittest` 風格撰寫)

### 系統架構 (Architecture)
- **`src/time_scheduler/scheduler.py`**：包含 `Scheduler` 類別，負責管理任務並執行背景迴圈 (background loop)。
- **`src/time_scheduler/task.py`**：包含 `Task` 類別，負責處理個別任務的狀態、計時邏輯與執行。
- **`src/time_scheduler/__init__.py`**：匯出公開 API。

## 專案結構與模組配置
此儲存庫是一個採用 `src/` 目錄結構的小型 Python 套件。核心程式碼位於 `src/time_scheduler/`，對外公開 API 由 `src/time_scheduler/__init__.py` 匯出。排程主迴圈實作在 `src/time_scheduler/scheduler.py`，任務狀態與執行邏輯則在 `src/time_scheduler/task.py`。測試放在 `tests/test_scheduler.py`。專案設定與相依性定義於 `pyproject.toml`，`uv.lock` 則記錄鎖定的開發環境。

### 目錄結構
- `src/time_scheduler/`：核心程式碼。
- `tests/`：單元測試與整合測試。
- `openspec/`：包含規格說明與變更紀錄 (採用 OpenSpec 工作流)。
- `.gemini/`, `.cline/`, `.agent/`：工具相關配置與技能定義。

## 建置、測試與開發指令
請使用 `pyproject.toml` 中宣告的 Python 3.13。

- `uv sync --dev`：安裝套件與開發相依性。
- `uv run pytest -q`：執行完整測試套件。
- `python -m pytest -q`：若本機沒有 `uv`，但已安裝相依性，可用此指令執行測試。
- `pip install -e .`：以 editable mode 安裝套件，方便本地開發。
- `python -m src.time_scheduler.example`：執行範例程式 (參考 README)。

請在專案根目錄執行上述指令，確保 `src/` 下的匯入路徑能正確解析。

## 程式風格與命名慣例
遵循目前的 Python 風格：
- **縮排 (Indentation)：** 4 個空格。
- **命名慣例 (Naming)：**
  - 模組 (Modules)：`snake_case` (例如：`time_scheduler`)
  - 類別 (Classes)：`PascalCase` (例如：`Scheduler`, `Task`)
  - 函式/方法 (Functions/Methods)：`snake_case` (例如：`add_task`, `get_tasks`)
- **型別提示 (Type Hinting)：** 公開方法與複雜邏輯必須使用型別註解。
- **簡潔原則 (Simplicity)：** 保持直觀且簡潔的風格，避免過度抽象化。
- 類別職責單一，並在可行時為公開方法補上型別註記。

## 測試指南
目前測試以 `unittest` 風格撰寫，並透過 `pytest` 執行。
- **位置：** 所有測試應放置於 `tests/` 目錄。
- **命名：** 檔案名稱應符合 `test_*.py` 格式，測試方法名稱可參考 `test_interval_execution` 這類具體描述。
- **測試涵蓋範圍：** 優先測試任務計時 (timing)、回呼函式 (callbacks) 以及排程器的生命週期 (start/stop)。
- **Bug 修復：** 修復 Bug 時務必包含回歸測試 (regression test)，應在修改程式碼前或同時補上回歸測試。

## 開發流程規範
所有功能開發必須嚴格依照 **SDD (Specification-Driven Development) 規格驅動開發** 與 **TDD (Test-Driven Development) 測試驅動開發** 順序執行：
1.  先建立規格文件，明確定義功能需求、API 介面與預期行為
2.  根據規格撰寫對應的測試案例，確保測試能完整驗證規格內容
3.  撰寫功能實作程式碼，直到所有測試案例通過
4.  驗證實作符合規格定義後，才可以進行後續提交作業

## Commit 與 Pull Request 指南
- **Commit 訊息：** 遵循 Conventional Commits 規範 (例如：`feat:`, `fix:`, `docs:`)。請讓訊息具體明確，例如 `fix: prevent duplicate startup execution`。
- **分支命名：** 使用具描述性的分支名稱。
- Pull Request 應包含變更摘要、修改原因、測試結果，以及任何會影響 API 的使用範例。若變更會影響文件或使用方式，請在同一個 PR 中同步更新 `README.md`。

## 貢獻補充說明
撰寫範例或測試時，請優先使用實際套件匯入路徑 `time_scheduler`。除非需求明確需要擴充架構，否則請維持此函式庫以記憶體運作、低相依性的設計方向。

請參考 `README.md` 以取得完整的「快速開始」指南與 API 範例。本函式庫設計為可供其他 Python 專案匯入使用的模組。