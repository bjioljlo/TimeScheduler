# 任務錯誤處理與重試機制實作任務

## 任務列表

### 1. 修改 Task 類別
- [x] 在 `__init__` 中新增 `max_retries`, `retry_delay`, `on_failure` 參數。
- [x] 新增 `retry_count` 屬性。
- [x] 修改 `execute` 方法：捕捉異常後，檢查重試邏輯。
- [x] 若需重試，設定 `next_run_time` 並增加 `retry_count`。
- [x] 若重試耗盡，觸發 `on_failure` 並重置 `retry_count`。

### 2. 修改 Scheduler 類別
- [x] 在 `add_task` 方法中新增 `max_retries`, `retry_delay`, `on_failure` 參數。
- [x] 傳遞參數到 `Task` 建構子。

### 3. 撰寫測試案例
- [x] 測試無重試：任務失敗後不重試。
- [x] 測試重試成功：任務失敗後重試並成功。
- [x] 測試重試失敗：重試耗盡後觸發 `on_failure`。
- [x] 測試延遲重試：檢查重試間隔。
- [x] 測試重複任務：重試不影響定時執行。
- [x] 測試回呼：`on_failure` 正確觸發。

### 4. 驗證與整合
- [x] 執行所有測試，確保通過。
- [x] 更新 README.md（若需）。
- [x] 檢查多執行緒安全。

## 完成條件
- [x] 所有測試通過。
- [x] 功能符合 proposal 和 design。
- [x] 無回歸問題。