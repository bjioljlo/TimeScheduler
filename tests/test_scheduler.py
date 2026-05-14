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

class TestTaskPriority(unittest.TestCase):
    def setUp(self):
        self.scheduler = Scheduler()
        self.executed_tasks = []

    def tearDown(self):
        self.scheduler.stop()

    def dummy_task(self, name):
        self.executed_tasks.append(name)

    def test_valid_priority_values(self):
        """3.1 測試有效的優先級參數"""
        from time_scheduler.task import Task

        high_task = Task("high", self.dummy_task, priority="high", args=("high",))
        med_task = Task("medium", self.dummy_task, priority="medium", args=("medium",))
        low_task = Task("low", self.dummy_task, priority="low", args=("low",))

        self.assertEqual(high_task.priority, "high")
        self.assertEqual(med_task.priority, "medium")
        self.assertEqual(low_task.priority, "low")

    def test_invalid_priority_value(self):
        """3.1 測試無效的優先級參數會拋出 ValueError"""
        from time_scheduler.task import Task

        with self.assertRaises(ValueError):
            Task("invalid", self.dummy_task, priority="invalid", args=("invalid",))

        with self.assertRaises(ValueError):
            Task("empty", self.dummy_task, priority="", args=("empty",))

    def test_default_priority(self):
        """3.4 測試預設優先級為 medium"""
        from time_scheduler.task import Task

        task = Task("default", self.dummy_task, args=("default",))
        self.assertEqual(task.priority, "medium")

    def test_scheduler_default_priority(self):
        """3.4 測試 add_task 預設優先級為 medium"""
        task_id = self.scheduler.add_task("default", self.dummy_task, args=("default",))
        tasks = self.scheduler.get_tasks()
        task_info = next(t for t in tasks if t["id"] == task_id)
        self.assertEqual(task_info["priority"], "medium")

    def test_priority_execution_order(self):
        """3.2 測試高優先級任務先執行"""
        # 用 run_on_startup 讓所有任務立即執行
        self.scheduler.add_task("low", self.dummy_task, run_on_startup=True,
                                priority="low", args=("low",))
        time.sleep(0.05)
        self.scheduler.add_task("high", self.dummy_task, run_on_startup=True,
                                priority="high", args=("high",))
        time.sleep(0.05)
        self.scheduler.add_task("medium", self.dummy_task, run_on_startup=True,
                                priority="medium", args=("medium",))

        self.scheduler.start()
        time.sleep(0.5)

        # 高優先級應先執行，然後 medium，最後 low
        high_idx = self.executed_tasks.index("high") if "high" in self.executed_tasks else -1
        med_idx = self.executed_tasks.index("medium") if "medium" in self.executed_tasks else -1
        low_idx = self.executed_tasks.index("low") if "low" in self.executed_tasks else -1

        self.assertGreater(high_idx, -1, "high priority task should execute")
        self.assertGreater(med_idx, -1, "medium priority task should execute")
        self.assertGreater(low_idx, -1, "low priority task should execute")

        self.assertLess(high_idx, med_idx, "high priority should execute before medium")
        self.assertLess(med_idx, low_idx, "medium priority should execute before low")

    def test_same_priority_fifo_order(self):
        """3.3 測試同優先級 FIFO 順序"""
        # 依序加入三個 medium 優先級的任務
        for i in range(3):
            self.scheduler.add_task(f"task_{i}", self.dummy_task,
                                    run_on_startup=True, priority="medium",
                                    args=(f"task_{i}",))

        self.scheduler.start()
        time.sleep(0.5)

        # 確認執行順序與加入順序相同
        for i in range(3):
            task_name = f"task_{i}"
            self.assertIn(task_name, self.executed_tasks,
                          f"{task_name} should be in executed tasks")

        # 檢查 FIFO 順序
        if len(self.executed_tasks) >= 3:
            self.assertEqual(self.executed_tasks[0], "task_0")
            self.assertEqual(self.executed_tasks[1], "task_1")
            self.assertEqual(self.executed_tasks[2], "task_2")


if __name__ == "__main__":
    unittest.main()
