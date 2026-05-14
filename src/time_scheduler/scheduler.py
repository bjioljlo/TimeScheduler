import threading
import time
from typing import Callable, Optional, List, Dict, Any, Literal
from .task import Task, Priority

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
        priority: Priority = "medium"
    ) -> str:
        """
        新增排程任務
        :param priority: 任務優先級 ("high", "medium", "low")，預設 "medium"
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
            priority=priority
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

    def get_tasks(self) -> List[Dict[str, Any]]:
        """
        取得目前所有任務的狀態
        """
        with self._lock:
            return [
                {
                    "id": t.id,
                    "name": t.name,
                    "priority": t.priority,
                    "next_run_time": t.next_run_time,
                    "interval_seconds": t.interval_seconds,
                    "is_running": t.is_running,
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

    @staticmethod
    def _priority_key(task: Task) -> int:
        """回傳優先級排序鍵值：高=0, 中=1, 低=2"""
        order = {"high": 0, "medium": 1, "low": 2}
        return order.get(task.priority, 1)

    def _run_loop(self):
        while self._running:
            tasks_to_run = []
            tasks_to_remove = []

            with self._lock:
                for task in self._tasks.values():
                    if task.should_run():
                        tasks_to_run.append(task)
                    # 自動清理已完成的任務 (next_run_time is None 且非執行中)
                    elif task.next_run_time is None and not task.is_running:
                        tasks_to_remove.append(task.id)

                # 安全移除已完成任務
                for task_id in tasks_to_remove:
                    del self._tasks[task_id]

            # 按優先級排序：高優先級先執行，同優先級保持 FIFO 順序
            tasks_to_run.sort(key=self._priority_key)

            # 使用新執行緒執行任務以避免阻塞其他排程
            for task in tasks_to_run:
                threading.Thread(target=task.execute, daemon=True).start()

            # 避免過度消耗 CPU
            time.sleep(0.1)
