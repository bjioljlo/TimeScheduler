# 任務錯誤處理與重試機制提案

## 功能概述
為 TimeScheduler 添加任務錯誤處理與重試機制，當任務執行失敗時，能夠自動重試指定次數，並在最終失敗後觸發回呼函式。這將提升套件的可靠性，特別適用於網路請求或外部依賴的任務。

## 需求描述
- **重試邏輯**：任務失敗時，自動重試最多 N 次（預設 0，即無重試）。
- **延遲重試**：每次重試間隔可設定延遲時間（預設 0 秒）。
- **最終失敗處理**：重試耗盡後，觸發 `on_failure` 回呼（可選）。
- **狀態追蹤**：記錄重試次數，並更新 `error_count`。
- **相容性**：保持向後相容，不影響現有任務。

## 預期行為
- 任務執行失敗時，若 `max_retries > 0`，則排程重試。
- 重試間隔後重新執行任務。
- 若重試仍失敗，觸發 `on_failure` 回呼，並停止重試。
- 重複任務（interval_seconds）在每次執行失敗後重試，但不影響下次定時執行。

## 範例使用
```python
scheduler.add_task(
    "unstable_task",
    lambda: requests.get("http://unstable-api.com"),
    interval_seconds=60,
    max_retries=3,
    retry_delay=5,
    on_failure=lambda name: print(f"Task {name} failed permanently")
)
```

## 風險與考量
- 避免無限重試：限制最大重試次數。
- 效能影響：重試可能增加 CPU/網路負載。
- 測試覆蓋：需測試重試邏輯、延遲與回呼。