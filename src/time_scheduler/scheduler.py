import threading
import time
from typing import Callable, Optional, List, Dict, Any
from .task import Task

class Scheduler:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_task(
        self,
        name: str,
        func: Callable,
        run_on_startup: bool = False,
        interval_seconds: Optional[int] = None,
        run_at: Optional[float] = None,
        args: tuple = (),
        kwargs: dict = None,
        on_start: Optional[Callable] = None,
        on_end: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None
    ) -> str:
        """
        新增排程任務
        :return: 任務的唯一 ID
        """
        task = Task(
            name=name,
            func=func,
            run_on_startup=run_on_startup,
            interval_seconds=interval_seconds,
            run_at=run_at,
            args=args,
            kwargs=kwargs,
            on_start=on_start,
            on_end=on_end,
            on_cancel=on_cancel
        )
        with self._lock:
            self._tasks[task.id] = task
        return task.id

    def remove_task(self, task_id: str) -> bool:
        """
        刪除排程任務
        :return: 成功回傳 True, 否則 False
        """
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        """
        取消指定的排程任務

        對於待處理（pending）的任務，直接從排程器中移除。
        對於執行中（running）的任務，設定取消旗標讓合作式取消生效。

        :param task_id: 任務的唯一 ID
        :return: 取消成功回傳 True，否則 False
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False

            if task.status == "pending":
                # 待處理任務：直接移除並觸發取消回呼
                task.status = "cancelled"
                task.cancel_event.set()
                if task.on_cancel:
                    try:
                        task.on_cancel(task.name)
                    except Exception as e:
                        print(f"Error in on_cancel callback for '{task.name}': {e}")
                del self._tasks[task_id]
                return True
            elif task.status == "running":
                # 執行中任務：設定取消事件，讓合作式取消生效
                task.cancel_event.set()
                task.status = "cancelled"
                # 不從 _tasks 移除，讓 execute 完成後清理
                return True
            else:
                # 已完成、已取消等狀態無法取消
                return False

    def get_tasks(self) -> List[Dict[str, Any]]:
        """
        取得目前所有任務的狀態
        """
        with self._lock:
            return [
                {
                    "id": t.id,
                    "name": t.name,
                    "next_run_time": t.next_run_time,
                    "interval_seconds": t.interval_seconds,
                    "status": t.status,
                    "last_run_time": t.last_run_time,
                    "run_count": t.run_count,
                    "error_count": t.error_count
                }
                for t in self._tasks.values()
            ]

    def start(self):
        """
        啟動背景排程器
        """
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """
        停止排程器
        """
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _run_loop(self):
        while self._running:
            tasks_to_run = []
            tasks_to_remove = []

            with self._lock:
                for task_id, task in list(self._tasks.items()):
                    if task.should_run():
                        tasks_to_run.append(task)
                    # 自動清理已完成的任務 (next_run_time is None 且非執行中)
                    elif task.next_run_time is None and not task.is_running:
                        tasks_to_remove.append(task_id)

                # 安全移除待清理任務
                for task_id in tasks_to_remove:
                    del self._tasks[task_id]

            # 使用新執行緒執行任務以避免阻塞其他排程
            for task in tasks_to_run:
                threading.Thread(target=task.execute, daemon=True).start()

            # 避免過度消耗 CPU
            time.sleep(0.1)