import unittest
import time
from time_scheduler import Scheduler

class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = Scheduler()
        self.executed_tasks = []

    def tearDown(self):
        self.scheduler.stop()

    def dummy_task(self, name):
        self.executed_tasks.append(name)

    def test_add_and_remove_task(self):
        task_id = self.scheduler.add_task("Test1", self.dummy_task, args=("Test1",))
        tasks = self.scheduler.get_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["name"], "Test1")

        success = self.scheduler.remove_task(task_id)
        self.assertTrue(success)
        self.assertEqual(len(self.scheduler.get_tasks()), 0)

    def test_callbacks(self):
        cb_events = []
        def on_start(name):
            cb_events.append(f"{name}_start")
        def on_end(name):
            cb_events.append(f"{name}_end")

        self.scheduler.add_task("CB_Task", self.dummy_task, run_on_startup=True, args=("CB_Task",), on_start=on_start, on_end=on_end)
        self.scheduler.start()
        time.sleep(0.5)
        self.assertIn("CB_Task_start", cb_events)
        self.assertIn("CB_Task", self.executed_tasks)
        self.assertIn("CB_Task_end", cb_events)

    def test_run_on_startup(self):
        self.scheduler.add_task("Startup", self.dummy_task, run_on_startup=True, args=("Startup",))
        self.scheduler.start()

        # 允許一些時間讓背景執行緒執行任務
        time.sleep(0.5)
        self.assertIn("Startup", self.executed_tasks)

    def test_delayed_execution(self):
        run_time = time.time() + 1.0
        self.scheduler.add_task("Delayed", self.dummy_task, run_at=run_time, args=("Delayed",))
        self.scheduler.start()

        # 0.5秒後還沒執行
        time.sleep(0.5)
        self.assertNotIn("Delayed", self.executed_tasks)

        # 再過0.8秒應該執行了
        time.sleep(0.8)
        self.assertIn("Delayed", self.executed_tasks)

    def test_interval_execution(self):
        self.scheduler.add_task("Interval", self.dummy_task, interval_seconds=1, args=("Interval",))
        self.scheduler.start()

        # 排程器剛加入尚未經過1秒，還沒執行
        time.sleep(0.1)
        self.assertNotIn("Interval", self.executed_tasks)

        # 等待超過1秒
        time.sleep(1.2)
        self.assertEqual(self.executed_tasks.count("Interval"), 1)

        # 再等待超過1秒
        time.sleep(1.2)
        self.assertEqual(self.executed_tasks.count("Interval"), 2)

    def test_retry_mechanism_no_retry(self):
        """測試無重試：任務失敗後不重試"""
        failure_events = []
        def failing_task(name):
            raise Exception("Task failed")
        def on_failure(name):
            failure_events.append(name)

        self.scheduler.add_task("NoRetry", failing_task, run_on_startup=True, args=("NoRetry",), max_retries=0, on_failure=on_failure)
        self.scheduler.start()
        time.sleep(0.5)
        self.assertIn("NoRetry", failure_events)

    def test_retry_mechanism_success_after_retry(self):
        """測試重試成功"""
        attempts = []
        def unstable_task(name):
            attempts.append(name)
            if len(attempts) < 2:
                raise Exception("Temporary failure")
            self.executed_tasks.append(name)  # 成功時記錄

        self.scheduler.add_task("RetrySuccess", unstable_task, run_on_startup=True, args=("RetrySuccess",), max_retries=3, retry_delay=0.1)
        self.scheduler.start()
        time.sleep(0.5)
        self.assertEqual(len(attempts), 2)  # 失敗一次，重試成功
        self.assertIn("RetrySuccess", self.executed_tasks)

    def test_retry_mechanism_failure_after_max_retries(self):
        """測試重試失敗：耗盡重試後觸發 on_failure"""
        attempts = []
        failure_events = []
        def always_failing_task(name):
            attempts.append(name)
            raise Exception("Always fails")
        def on_failure(name):
            failure_events.append(name)

        self.scheduler.add_task("RetryFail", always_failing_task, run_on_startup=True, args=("RetryFail",), max_retries=2, retry_delay=0.1, on_failure=on_failure)
        self.scheduler.start()
        time.sleep(0.5)
        self.assertEqual(len(attempts), 3)  # 初始 + 2次重試
        self.assertIn("RetryFail", failure_events)

    def test_retry_delay(self):
        """測試重試延遲"""
        start_time = time.time()
        attempts = []
        def failing_task(name):
            attempts.append(time.time() - start_time)
            raise Exception("Fails")

        self.scheduler.add_task("RetryDelay", failing_task, run_on_startup=True, args=("RetryDelay",), max_retries=1, retry_delay=0.2, on_failure=lambda n: None)
        self.scheduler.start()
        time.sleep(0.5)
        self.assertGreaterEqual(len(attempts), 2)
        if len(attempts) >= 2:
            self.assertGreaterEqual(attempts[1] - attempts[0], 0.2)

if __name__ == "__main__":
    unittest.main()
