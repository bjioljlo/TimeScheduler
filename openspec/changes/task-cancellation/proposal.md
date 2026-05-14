# 任務取消與中斷提案

## Why

TimeScheduler 目前無法取消已排程但尚未執行的任務，或中斷正在執行的任務。在長時間運行的任務或系統需要快速響應的情況下，這會造成問題。添加任務取消功能能提升系統的靈活性與響應性。

## What Changes

- 新增 `cancel_task()` 方法到 `Scheduler`，允許取消排程任務
- 新增任務狀態追蹤（pending, running, cancelled）
- 新增 `on_cancel` 回呼函式
- 支援中斷正在執行的任務（使用執行緒事件）

## Capabilities

### New Capabilities
- `task-cancellation`: 任務取消與中斷管理功能

### Modified Capabilities
<!-- 無現有能力被修改 -->

## Impact

- 影響 `Scheduler` 類別的任務管理邏輯
- 影響 `Task` 類別的狀態管理
- 需要更新測試案例和文檔
- 無外部依賴變化