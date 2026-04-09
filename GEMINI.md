# TimeScheduler 專案上下文 (Project Context)

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

## 建置與運行 (Building and Running)
本專案使用 `uv` 進行相依性管理與建置。

### 常用指令
- **安裝開發環境：** `uv sync --dev` 或 `pip install -e .`
- **執行測試：** `uv run pytest -q` 或 `python -m pytest -q`
- **執行範例 (參考 README)：** `python -m src.time_scheduler.example` (或根據範例程式碼位置調整)。

## 開發規範 (Development Conventions)

### 程式風格 (Coding Style)
- **縮排 (Indentation)：** 4 個空格。
- **命名慣例 (Naming)：**
  - 模組 (Modules)：`snake_case` (例如：`time_scheduler`)
  - 類別 (Classes)：`PascalCase` (例如：`Scheduler`, `Task`)
  - 函式/方法 (Functions/Methods)：`snake_case` (例如：`add_task`, `get_tasks`)
- **型別提示 (Type Hinting)：** 公開方法與複雜邏輯必須使用型別註解。
- **簡潔原則 (Simplicity)：** 保持直觀且簡潔的風格，避免過度抽象化。

### 測試實務 (Testing Practices)
- **位置：** 所有測試應放置於 `tests/` 目錄。
- **框架：** 使用 `unittest` 風格的類別，並透過 `pytest` 執行。
- **命名：** 檔案名稱應符合 `test_*.py` 格式。
- **測試涵蓋範圍：** 優先測試任務計時 (timing)、回呼函式 (callbacks) 以及排程器的生命週期 (start/stop)。
- **Bug 修復：** 修復 Bug 時務必包含回歸測試 (regression test)。

### Git 規範
- **Commit 訊息：** 遵循 Conventional Commits 規範 (例如：`feat:`, `fix:`, `docs:`)。
- **分支命名：** 使用具描述性的分支名稱。

## 專案結構 (Project Structure)
- `src/time_scheduler/`：核心程式碼。
- `tests/`：單元測試與整合測試。
- `openspec/`：包含規格說明與變更紀錄 (採用 OpenSpec 工作流)。
- `.gemini/`, `.cline/`, `.agent/`：工具相關配置與技能定義。

## 使用說明 (Usage)
請參考 `README.md` 以取得完整的「快速開始」指南與 API 範例。本函式庫設計為可供其他 Python 專案匯入使用的模組。
