import threading
import time
import uuid
from typing import Callable, Optional


class CancelToken:
    """合作式取消令牌，提供給任務函式檢查取消狀態"""

    def __init__(self, event: threading.Event):
        self._event = event

    def is_cancelled(self) -> bool:
        """檢查是否已被要求取消"""
        return self._event.is_set()


class Task:
    def __init__(
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
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.func = func
        self.run_on_startup = run_on_startup
        self.interval_seconds = interval_seconds
        self.run_at = run_at
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.on_start = on_start
        self.on_end = on_end
        self.on_cancel = on_cancel

        self.status = "pending"  # pending, running, cancelled, completed
        self.cancel_event = threading.Event()
        self.has_run_startup = False
        self.last_run_time: Optional[float] = None
        self.run_count = 0
        self.error_count = 0
        self.next_run_time = self._calculate_next_run()

    @property
    def is_running(self) -> bool:
        return self.status == "running"

    def _calculate_next_run(self) -> Optional[float]:
        now = time.time()

        if self.run_on_startup and not self.has_run_startup:
            return now

        if self.run_at is not None:
            if self.run_at > now:
                return self.run_at
            elif self.interval_seconds is None:
                # 單次任務已過期且無重複間隔
                return None

        if self.interval_seconds is not None:
            if self.last_run_time is None:
                return now + self.interval_seconds
            else:
                next_run = self.last_run_time + self.interval_seconds
                # 若延遲超過2倍間隔則重置到現在時間開始
                if next_run + (self.interval_seconds * 2) < now:
                    return now + self.interval_seconds
                return next_run

        return None

    def should_run(self) -> bool:
        if self.status != "pending":
            return False
        if self.next_run_time is None:
            return False
        return time.time() >= self.next_run_time

    def execute(self):
        """執行任務，支援合作式取消"""
        self.status = "running"
        try:
            if self.on_start:
                try:
                    self.on_start(self.name)
                except Exception as e:
                    print(f"Error in on_start callback for '{self.name}': {e}")

            # 檢查執行前是否已被取消
            if self.cancel_event.is_set():
                self.status = "cancelled"
            else:
                try:
                    # 建立取消令牌並傳遞給任務函式（若函式接受 cancel_token 參數）
                    import inspect
                    token = CancelToken(self.cancel_event)
                    sig = inspect.signature(self.func)
                    if "cancel_token" in sig.parameters:
                        self.func(*self.args, **self.kwargs, cancel_token=token)
                    else:
                        self.func(*self.args, **self.kwargs)
                    self.run_count += 1
                except Exception as e:
                    self.error_count += 1
                    print(f"Error executing task '{self.name}': {e}")

            if self.on_end:
                try:
                    self.on_end(self.name)
                except Exception as e:
                    print(f"Error in on_end callback for '{self.name}': {e}")

            # 更新任務狀態
            if self.status == "cancelled":
                if self.on_cancel:
                    try:
                        self.on_cancel(self.name)
                    except Exception as e:
                        print(f"Error in on_cancel callback for '{self.name}': {e}")
                self.next_run_time = None
            else:
                # 標記已執行過啟動任務
                if self.run_on_startup and not self.has_run_startup:
                    self.has_run_startup = True

                self.last_run_time = time.time()

                # 重新計算下一次執行時間
                self.next_run_time = self._calculate_next_run()

                if self.next_run_time is None:
                    self.status = "completed"
                else:
                    self.status = "pending"
        finally:
            # 確保如果執行中發生意外取消，狀態仍正確
            if self.status == "running":
                self.status = "completed"