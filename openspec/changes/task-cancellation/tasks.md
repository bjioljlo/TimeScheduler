# 任務取消與中斷實作任務

## 1. 修改 Task 類別
- [x] 1.1 新增狀態屬性（pending, running, cancelled, completed）
- [x] 1.2 新增取消事件（threading.Event）
- [x] 1.3 在 `__init__` 中新增 `on_cancel` 參數
- [x] 1.4 修改 `execute` 方法處理取消邏輯

## 2. 修改 Scheduler 類別
- [x] 2.1 新增 `cancel_task(task_id)` 方法
- [x] 2.2 在 `add_task` 方法中新增 `on_cancel` 參數
- [x] 2.3 傳遞取消事件到任務函式

## 3. 撰寫測試案例
- [x] 3.1 測試取消待處理任務
- [x] 3.2 測試取消不存在的任務
- [x] 3.3 測試取消執行中任務（合作式）
- [x] 3.4 測試取消回呼觸發

## 4. 驗證與整合
- [x] 4.1 執行所有測試，確保通過
- [x] 4.2 更新 README.md（若需）
- [x] 4.3 檢查多執行緒安全
