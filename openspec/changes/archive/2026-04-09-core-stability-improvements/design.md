## Context

此變更針對 TimeScheduler 核心穩定性問題做修復，所有變更維持完全向後相容，不破壞現有 API 合約。目前程式碼基礎是穩定但缺少生產環境需要的基本防護機制。

## Goals / Non-Goals

**Goals:**
1. 預防任務重疊執行造成的資源競爭
2. 修正間隔排程隨任務執行時間漂移的問題
3. 自動清理已完成的單次任務避免記憶體洩漏
4. 提供基本任務執行狀態資訊
5. 所有變更維持 100% 向後相容性

**Non-Goals:**
1. 不新增任何公開 API 方法
2. 不變更現有預設行為
3. 不增加任何外部相依性
4. 不導入複雜的排程演算法

## Decisions

1. **任務執行防護**：在 Task 類別加入 boolean 旗標 `is_running`，`should_run()` 檢查時如果正在執行就回傳 False
2. **固定間隔計算**：間隔任務下次執行時間 = `next_run_time + interval_seconds`，而不是 `now() + interval_seconds`
3. **自動清理機制**：當 `next_run_time` 回傳 None 時，Scheduler 會在迴圈中自動移除該任務
4. **狀態欄位**：在 Task 加入 `last_run_time`、`run_count`、`error_count` 欄位做基本統計

## Risks / Trade-offs

| 風險 | 影響 | 緩解措施 |
|---|---|---|
| 執行中旗標可能發生死結 | 低 | 只在 execute() 進入與離開時設定，不做任何等待作業 |
| 固定間隔可能造成任務跳過 | 中 | 當延遲超過 2x 間隔時自動重置，避免累積延遲 |
| 自動移除任務可能打斷預期行為 | 低 | 只移除確定不會再執行的任務，可藉由 API 重新加入 |

## Migration Plan

此變更完全向後相容，不需要遷移步驟。升級後自動套用所有改進。