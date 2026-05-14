import time
import uuid
from typing import Callable, Optional

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
        max_retries: int = 0,
        retry_delay: float = 0.0,
        on_failure: Optional[Callable] = None
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
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.on_failure = on_failure

        self.has_run_startup = False
        self.is_running = False
        self.last_run_time: Optional[float] = None
        self.run_count = 0
        self.error_count = 0
        self.retry_count = 0
        self.next_run_time = self._calculate_next_run()

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
        if self.is_running:
            return False
        if self.next_run_time is None:
            return False
        return time.time() >= self.next_run_time

    def execute(self):
        """執行任務並計算下一次執行時間"""
        self.is_running = True
        try:
            if self.on_start and self.retry_count == 0:  # 只在首次執行觸發 on_start
                try:
                    self.on_start(self.name)
                except Exception as e:
                    print(f"Error in on_start callback for '{self.name}': {e}")

            try:
                self.func(*self.args, **self.kwargs)
                self.run_count += 1
                self.retry_count = 0  # 成功後重置重試計數
            except Exception as e:
                self.error_count += 1
                print(f"Error executing task '{self.name}': {e}")

                # 重試邏輯
                if self.retry_count < self.max_retries:
                    self.retry_count += 1
                    self.next_run_time = time.time() + self.retry_delay
                    print(f"Retrying task '{self.name}' (attempt {self.retry_count}/{self.max_retries}) in {self.retry_delay} seconds")
                    self.is_running = False
                    return  # 不繼續執行後續邏輯
                else:
                    # 重試耗盡，觸發 on_failure
                    if self.on_failure:
                        try:
                            self.on_failure(self.name)
                        except Exception as e:
                            print(f"Error in on_failure callback for '{self.name}': {e}")
                    self.retry_count = 0  # 重置重試計數

            if self.on_end and self.retry_count == 0:  # 只在成功或最終失敗後觸發 on_end
                try:
                    self.on_end(self.name)
                except Exception as e:
                    print(f"Error in on_end callback for '{self.name}': {e}")

            # 標記已執行過啟動任務
            if self.run_on_startup and not self.has_run_startup:
                self.has_run_startup = True

            self.last_run_time = time.time()

            # 重新計算下一次執行時間（僅在成功或重試耗盡後）
            if self.retry_count == 0:
                self.next_run_time = self._calculate_next_run()
        finally:
            self.is_running = False
