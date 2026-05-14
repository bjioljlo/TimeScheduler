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

    # ==== 任務取消測試 ====

    def test_cancel_pending_task(self):
        """測試取消待處理任務"""
        task_id = self.scheduler.add_task("CancelPending", self.dummy_task, args=("CancelPending",))
        # 確認任務存在
        self.assertEqual(len(self.scheduler.get_tasks()), 1)

        # 取消待處理任務
        result = self.scheduler.cancel_task(task_id)
        self.assertTrue(result)
        # 任務應從排程器中移除
        self.assertEqual(len(self.scheduler.get_tasks()), 0)

    def test_cancel_non_existent_task(self):
        """測試取消不存在的任務"""
        result = self.scheduler.cancel_task("non-existent-id")
        self.assertFalse(result)

    def test_cancel_running_task(self):
        """測試取消執行中任務（合作式取消）"""
        cancelled_flag = []

        def long_running_task(cancel_token):
            # 模擬長時間運作，並週期性檢查取消狀態
            while not cancel_token.is_cancelled():
                pass  # 等待取消
            self.executed_tasks.append("CancelledRunning")
            cancelled_flag.append(True)

        task_id = self.scheduler.add_task("LongTask", long_running_task, run_on_startup=True)
        self.scheduler.start()
        # 給任務一些時間開始執行
        time.sleep(0.3)

        # 確認任務狀態為 running
        tasks = self.scheduler.get_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["status"], "running")

        # 取消執行中任務
        result = self.scheduler.cancel_task(task_id)
        self.assertTrue(result)

        # 等待任務確實取消
        time.sleep(0.3)
        self.assertIn("CancelledRunning", self.executed_tasks)
        self.assertTrue(cancelled_flag)

    def test_cancel_callback(self):
        """測試取消回呼觸發"""
        cancel_events = []

        def on_cancel(name):
            cancel_events.append(f"{name}_cancelled")

        # 使用未來時間的任務確保它保持在 pending 狀態
        future_time = time.time() + 10.0
        task_id = self.scheduler.add_task(
            "CancelCB", self.dummy_task,
            args=("CancelCB",),
            on_cancel=on_cancel,
            run_at=future_time
        )
        # 不啟動排程器，任務保持在 pending 狀態
        self.assertEqual(len(self.scheduler.get_tasks()), 1)

        # 取消待處理任務
        result = self.scheduler.cancel_task(task_id)
        self.assertTrue(result)
        self.assertIn("CancelCB_cancelled", cancel_events)

if __name__ == "__main__":
    unittest.main()
