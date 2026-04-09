## Why

目前 TimeScheduler 核心實作存在數個穩定性問題，包括任務重疊執行、排程時間漂移、完成任務記憶體洩漏，這些問題在生產環境長時間執行時會造成嚴重影響。這些都是低風險高價值的修復，不需要改變 API 介面就可以大幅提升可靠度。

## What Changes

1. ✋ 防止任務重疊執行：同一時間同一個任務只會有一個執行個體在執行
2. ⏰ 修復間隔排程漂移：固定時間間隔而不是執行完成後才計算下次時間
3. 🧹 自動移除完成的單次任務：執行完畢的一次性任務會自動從排程器移除
4. 📊 基本任務狀態追蹤：記錄上次執行時間、執行次數、錯誤次數

所有變更皆完全向後相容，沒有破壞性變更。

## Capabilities

### New Capabilities
- `task-execution-guard`: 任務執行中防護機制
- `fixed-interval-scheduling`: 固定間隔排程邏輯
- `auto-task-cleanup`: 自動任務清理機制
- `task-status-tracking`: 任務執行狀態追蹤

### Modified Capabilities
(無)

## Impact

- 變更檔案：`src/time_scheduler/task.py`、`src/time_scheduler/scheduler.py`
- 所有公開 API 維持不變
- 現有測試全部可通過
- 不增加任何外部相依性
- 記憶體與 CPU 負荷影響可忽略