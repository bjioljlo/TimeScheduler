# TimeScheduler

TimeScheduler 是一個輕量級的 Python 排程任務套件，專注於提供簡單、易用的 API 讓開發者能夠在專案中管理定時與背景執行任務，完全基於記憶體運作，無外部資料庫依賴。

## 功能特色
- **啟動執行 (Run on Startup)**: 專案啟動時立刻執行一次。
- **定時執行 (Delayed Execution)**: 在未來的特定時間點執行。
- **重複執行 (Interval Execution)**: 每隔固定的時間間隔重複執行。

## 安裝方式

目前此套件僅供本地端開發使用，您可以在專案目錄下執行：
```bash
pip install -e .
```

## 快速開始

以下示範如何建立排程器並新增各種任務：

```python
import time
from TimeScheduler import Scheduler

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

    # 2. 定時執行任務 (3 秒後執行)
    scheduler.add_task(
        name="三秒後執行",
        func=my_task,
        run_at=time.time() + 3.0,
        args=("這是在三秒後觸發的！",)
    )

    # 3. 重複執行任務 (每隔 2 秒執行)
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

    print("排程器已啟動，按 Ctrl+C 結束。")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("正在停止排程器...")
        scheduler.stop()
```
