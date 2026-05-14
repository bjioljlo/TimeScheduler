# 任務優先級支援提案

## Why

TimeScheduler 目前以 FIFO（先進先出）方式執行任務，但在實際應用中，有些任務（如緊急通知、關鍵數據處理）需要優先執行。缺乏優先級支援會導致重要任務被延遲，影響系統可靠性。這個功能能讓用戶為任務設定優先級，提升排程器的實用性。

## What Changes

- 新增 `priority` 參數到 `Task` 和 `Scheduler.add_task()`，支援 "high", "medium", "low" 三個等級
- 修改 Scheduler 的任務執行邏輯，按優先級排序執行（高優先級先執行）
- 保持向後相容，預設優先級為 "medium"

## Capabilities

### New Capabilities
- `task-priority`: 任務優先級管理功能，允許設定和比較任務優先級

### Modified Capabilities
<!-- 無現有能力被修改 -->

## Impact

- 影響 `Scheduler` 類別的任務隊列管理邏輯
- 影響 `Task` 類別的初始化和比較方法
- 需要更新測試案例和文檔
- 無外部依賴變化