# 任務錯誤處理與重試機制設計

## API 設計

### Task 類別修改
新增參數：
- `max_retries: int = 0`：最大重試次數。
- `retry_delay: float = 0.0`：重試延遲秒數。
- `on_failure: Optional[Callable] = None`：最終失敗回呼。

新增屬性：
- `retry_count: int = 0`：當前重試次數。
- `is_retried: bool = False`：標記是否正在重試中。

### Scheduler 類別修改
`add_task` 方法新增參數：
- `max_retries: int = 0`
- `retry_delay: float = 0.0`
- `on_failure: Optional[Callable] = None`

## 架構設計

### 重試流程
1. 任務執行失敗（異常拋出）。
2. 若 `retry_count < max_retries`，增加 `retry_count`，設定 `next_run_time` 為 `time.time() + retry_delay`。
3. 若 `retry_count >= max_retries`，觸發 `on_failure` 回呼，重置 `retry_count` 為 0。
4. 對於重複任務，重試不影響下次定時執行。

### 狀態管理
- `error_count`：總錯誤次數（包括重試失敗）。
- `retry_count`：當前重試次數（每次成功執行後重置）。
- 確保多執行緒安全，使用現有鎖機制。

### 相容性
- 所有新參數預設為 0/None，保持向後相容。
- 現有任務無需修改。

## 實作細節
- 在 `Task.execute()` 中修改錯誤處理邏輯。
- 重試時不觸發 `on_start`/`on_end`，僅在最終失敗時觸發 `on_failure`。
- 延遲使用 `time.sleep` 或排程到下次檢查（避免阻塞）。