# Repository Guidelines

## 專案結構與模組配置
此儲存庫是一個採用 `src/` 目錄結構的小型 Python 套件。核心程式碼位於 `src/time_scheduler/`，對外公開 API 由 `src/time_scheduler/__init__.py` 匯出。排程主迴圈實作在 `src/time_scheduler/scheduler.py`，任務狀態與執行邏輯則在 `src/time_scheduler/task.py`。測試放在 `tests/test_scheduler.py`。專案設定與相依性定義於 `pyproject.toml`，`uv.lock` 則記錄鎖定的開發環境。

## 建置、測試與開發指令
請使用 `pyproject.toml` 中宣告的 Python 3.13。

- `uv sync --dev`：安裝套件與開發相依性。
- `uv run pytest -q`：執行完整測試套件。
- `python -m pytest -q`：若本機沒有 `uv`，但已安裝相依性，可用此指令執行測試。
- `pip install -e .`：以 editable mode 安裝套件，方便本地開發。

請在專案根目錄執行上述指令，確保 `src/` 下的匯入路徑能正確解析。

## 程式風格與命名慣例
遵循目前的 Python 風格：使用 4 個空白縮排、類別職責單一，並在可行時為公開方法補上型別註記。模組名稱使用全小寫加底線，例如 `time_scheduler`；類別使用 `PascalCase`，例如 `Scheduler`、`Task`；函式與方法使用 `snake_case`，例如 `add_task`、`get_tasks`。請維持現有程式碼直接、簡潔的風格，避免引入不必要的抽象層。

## 測試指南
目前測試以 `unittest` 風格撰寫，並透過 `pytest` 執行。新增測試時，請放在 `tests/` 下，檔名使用 `test_*.py`，測試方法名稱可參考 `test_interval_execution` 這類具體描述。請優先覆蓋任務排程時間、回呼函式以及排程器啟動與停止等行為。若修正 bug，應在修改程式碼前或同時補上回歸測試。

## Commit 與 Pull Request 指南
近期提交紀錄使用 Conventional Commit 前綴，例如 `feat:`、`fix:`。請延續這種格式，並讓訊息具體明確，例如 `fix: prevent duplicate startup execution`。Pull Request 應包含變更摘要、修改原因、測試結果，以及任何會影響 API 的使用範例。若變更會影響文件或使用方式，請在同一個 PR 中同步更新 `README.md`。

## 貢獻補充說明
撰寫範例或測試時，請優先使用實際套件匯入路徑 `time_scheduler`。除非需求明確需要擴充架構，否則請維持此函式庫以記憶體運作、低相依性的設計方向。
