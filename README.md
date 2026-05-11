# TimeScheduler

TimeScheduler 是一個輕量級、基於記憶體 (memory-based) 的 Python 任務排程套件。它提供簡單的 API 讓開發者能夠在專案中管理定時與背景執行任務，無需依賴外部資料庫。

## 功能特色

- **啟動執行 (Run on Startup)** — 排程器啟動時立刻執行一次
- **定時執行 (Delayed Execution)** — 在未來的特定時間點執行
- **重複執行 (Interval Execution)** — 每隔固定的時間間隔重複執行
- **回呼函式 (Callbacks)** — 支援任務開始前 (`on_start`) 與任務結束後 (`on_end`) 的回呼
- **任務管理** — 支援動態新增、刪除與查詢任務狀態
- **執行緒安全** — 內部使用鎖機制 (`threading.Lock`) 保護共享資源
- **自動清理** — 已完成的單次任務會自動從排程器中移除

## 安裝方式

### 使用 pip（本地開發）

```bash
pip install -e .
```

### 使用 uv（推薦）

```bash
uv sync --dev
```

### 使用 pip 從專案目錄安裝

```bash
pip install -e .
```

## 快速開始

以下示範如何建立排程器並新增各種類型的任務：

```python
import time
from time_scheduler import Scheduler

def my_task(msg):
    print(f"[{time.strftime('%H:%M:%S')}] 任務執行：{msg}")

if __name__ == "__main__":
    # 建立並啟動 Scheduler
    scheduler = Scheduler()
    scheduler.start()

    # 1. 啟動執行任務
    scheduler.add_task(
        name="立刻執行",
        func=my_task,
        run_on_startup=True,
        args=("啟動時要執行的任務",)
    )

    # 2. 定時執行任務（3 秒後執行）
    scheduler.add_task(
        name="三秒後執行",
        func=my_task,
        run_at=time.time() + 3.0,
        args=("這是在三秒後觸發的！",)
    )

    # 3. 重複執行任務（每隔 2 秒執行）
    scheduler.add_task(
        name="每兩秒執行",
        func=my_task,
        interval_seconds=2,
        args=("這是一個重複任務",)
    )

    # 4. 帶有回呼函式 (Callbacks) 的任務
    def on_task_start(name):
        print(f"[{time.strftime('%H:%M:%S')}] --- 任務 '{name}' 準備開始 ---")

    def on_task_end(name):
        print(f"[{time.strftime('%H:%M:%S')}] --- 任務 '{name}' 執行完畢 ---")

    scheduler.add_task(
        name="回呼示範",
        func=my_task,
        run_at=time.time() + 1.0,
        args=("附帶 Callback 的任務",),
        on_start=on_task_start,
        on_end=on_task_end
    )

    # 5. 使用 kwargs 傳遞關鍵字參數
    def task_with_kwargs(greeting, name):
        print(f"[{time.strftime('%H:%M:%S')}] {greeting}, {name}!")

    scheduler.add_task(
        name="kwargs 示範",
        func=task_with_kwargs,
        run_on_startup=True,
        kwargs={"greeting": "Hello", "name": "TimeScheduler"}
    )

    print("排程器已啟動，按 Ctrl+C 結束。")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("正在停止排程器...")
        scheduler.stop()
```

## API 參考

### `Scheduler` 類別

#### `Scheduler()`

建立一個新的排程器實例。

```python
scheduler = Scheduler()
```

#### `add_task(name, func, ...) -> str`

新增一個排程任務，回傳該任務的唯一 ID（UUID 字串）。

| 參數 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `name` | `str` | — | 任務名稱（僅供識別用） |
| `func` | `Callable` | — | 要執行的函式 |
| `run_on_startup` | `bool` | `False` | 是否在排程器啟動後立即執行一次 |
| `run_at` | `float \| None` | `None` | 指定未來執行時間（Unix timestamp） |
| `interval_seconds` | `int \| None` | `None` | 重複執行的間隔秒數 |
| `args` | `tuple` | `()` | 傳遞給 `func` 的位置參數 |
| `kwargs` | `dict \| None` | `None` | 傳遞給 `func` 的關鍵字參數 |
| `on_start` | `Callable \| None` | `None` | 任務開始前的回呼函式，回傳任務名稱 |
| `on_end` | `Callable \| None` | `None` | 任務結束後的回呼函式，回傳任務名稱 |

#### `remove_task(task_id: str) -> bool`

刪除指定的排程任務。成功回傳 `True`，若任務不存在則回傳 `False`。

```python
task_id = scheduler.add_task("my_task", my_func, run_on_startup=True)
scheduler.remove_task(task_id)  # True
scheduler.remove_task("non_existent_id")  # False
```

#### `get_tasks() -> List[Dict[str, Any]]`

取得目前所有任務的狀態列表。每個任務包含以下欄位：

| 欄位 | 型別 | 說明 |
|------|------|------|
| `id` | `str` | 任務唯一 ID |
| `name` | `str` | 任務名稱 |
| `next_run_time` | `float \| None` | 下次執行時間（Unix timestamp），若為 `None` 表示不再執行 |
| `interval_seconds` | `int \| None` | 重複間隔秒數 |
| `is_running` | `bool` | 任務是否正在執行中 |
| `last_run_time` | `float \| None` | 最後一次執行時間 |
| `run_count` | `int` | 已執行次數 |
| `error_count` | `int` | 執行錯誤次數 |

```python
tasks = scheduler.get_tasks()
for task in tasks:
    print(f"{task['name']}: 已執行 {task['run_count']} 次，錯誤 {task['error_count']} 次")
```

#### `start()`

啟動背景排程執行緒。若已啟動則無作用。

```python
scheduler.start()
```

#### `stop()`

停止排程器，等待背景執行緒結束（最多等待 2 秒）。

```python
scheduler.stop()
```

### `Task` 類別

如果需要直接操作任務物件，也可以手動建立 `Task` 實例。`Task` 的建構子參數與 `Scheduler.add_task()` 相同。

```python
from time_scheduler import Task

task = Task(
    name="手動任務",
    func=my_func,
    run_on_startup=True,
    args=("hello",),
    kwargs={"key": "value"},
    on_start=lambda name: print(f"{name} 開始"),
    on_end=lambda name: print(f"{name} 結束")
)

print(task.id)         # 唯一識別碼 (UUID)
print(task.run_count)  # 執行次數
```

## 任務管理範例

```python
import time
from time_scheduler import Scheduler

scheduler = Scheduler()
scheduler.start()

# 新增任務
task_id = scheduler.add_task(
    name="可管理任務",
    func=lambda msg: print(msg),
    interval_seconds=2,
    args=("每隔 2 秒執行一次",)
)

# 查詢任務狀態
tasks = scheduler.get_tasks()
print(f"目前有 {len(tasks)} 個任務")

# 等待一段時間後刪除任務
time.sleep(5)
scheduler.remove_task(task_id)
print(f"任務已刪除，剩餘 {len(scheduler.get_tasks())} 個任務")

scheduler.stop()
```

## 開發者指引

### 環境需求

- Python >= 3.13
- 建議使用 [uv](https://docs.astral.sh/uv/) 管理虛擬環境與相依性

### 安裝開發相依性

```bash
uv sync --dev
```

### 執行測試

```bash
uv run pytest -q
```

或使用 pip 安裝相依性後執行：

```bash
python -m pytest -q
```

### 貢獻方式

1. Fork 此儲存庫
2. 建立您的功能分支：`git checkout -b feat/my-feature`
3. 撰寫規格文件（請參考 `openspec/` 目錄）
4. 根據規格撰寫測試案例
5. 實作功能並確保所有測試通過
6. 提交 Pull Request

本專案遵循 **規格驅動開發 (SDD)** 與 **測試驅動開發 (TDD)** 流程，所有功能開發前必須先建立規格文件與測試案例。

## 授權

本專案為 MIT 授權。