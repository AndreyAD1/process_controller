import unittest
import time

from main import ProcessController


def test_task(timeout):
    time.sleep(timeout)


def test_task_error():
    raise Exception("test error")


class TestProcessController(unittest.TestCase):
    def test_start_empty(self):
        pc = ProcessController()
        pc.set_max_proc(4)
        pc.start([], 2)
        self.assertEqual(pc.wait_count(), 0)
        self.assertEqual(pc.alive_count(), 0)
        pc.wait()
        self.assertEqual(pc.wait_count(), 0)
        self.assertEqual(pc.alive_count(), 0)

    def test_common_start(self):
        pc = ProcessController()
        pc.set_max_proc(3)
        pc.start(
            [
                (test_task, (2,)),
                (test_task, (10,)),
                (test_task, (3,)),
                # (test_task_error, tuple()),
                (test_task, (3,)),
                (test_task, (1,)),
            ],
            5
        )
        time.sleep(0.1)
        self.assertEqual(pc.wait_count(), 2)
        self.assertEqual(pc.alive_count(), 3)

        time.sleep(2)
        self.assertEqual(pc.wait_count(), 1)
        self.assertEqual(pc.alive_count(), 3)

        time.sleep(1)
        self.assertEqual(pc.wait_count(), 0)
        self.assertEqual(pc.alive_count(), 3)

        time.sleep(1)
        self.assertEqual(pc.wait_count(), 0)
        self.assertEqual(pc.alive_count(), 2)

        pc.wait()
        self.assertEqual(pc.wait_count(), 0)
        self.assertEqual(pc.alive_count(), 0)


if __name__ == "__main__":
    unittest.main()
