import multiprocessing as mp
import os
import time
from threading import Thread


def get_test_task(timeout):
    print(f"start to sleep {timeout} s : {os.getpid()}")
    time.sleep(timeout)
    print(f"wake up after {timeout} s : {os.getpid()}")


def another_task(a, b, c):
    time.sleep(2)
    print("calculation result: ", a * b - c)


# task_counter_lock = mp.Lock()
# runner_counter_lock = mp.Lock()
# MAX_TIMEOUT = 4
# tasks = [
#     (get_test_task, 5),
#     (get_test_task, 2,),
#     (get_test_task, 1,),
#     (get_test_task, 3,),
#     (get_test_task, 0.5,)
# ]
# task_counter = len(tasks)
# runner_counter = 0


class ProcessController:
    def __init__(self):
        self.task_counter_lock = mp.Lock()
        self.runner_counter_lock = mp.Lock()
        self.task_counter = 0
        self.runner_counter = 0
        self.max_timeout = None
        self.max_process_number = None
        self._result = None
        self._process_pool = None

    def set_max_proc(self, max_process):
        self.max_process_number = max_process

    def _complete_runner(self):
        self.runner_counter_lock.acquire()
        self.runner_counter -= 1
        self.runner_counter_lock.release()

    def runner(self, func, *args):
        self.task_counter_lock.acquire()
        self.runner_counter_lock.acquire()
        try:
            task_thread = Thread(target=func, args=args)
            task_thread.start()
            self.task_counter -= 1
            self.runner_counter += 1
        finally:
            self.task_counter_lock.release()
            self.runner_counter_lock.release()

        task_thread.join(self.max_timeout)

    def start(self, tasks, max_timeout):
        self.max_timeout = max_timeout
        updated_tasks = ...
        process_pool = mp.Pool(processes=self.max_process_number)
        result = process_pool.starmap_async(
            self.runner,
            updated_tasks,
            callback=self._complete_runner,
            error_callback=self._complete_runner
        )
        self._process_pool = process_pool
        self._result = result

    def wait(self):
        self._result.join()
        self._process_pool.close()
        self._process_pool.join()

    def alive_count(self):
        return self.runner_counter

    def wait_count(self):
        return self.task_counter


def main():
    process_controller = ProcessController()
    process_controller.set_max_proc(3)
    process_controller.start(
        [
            (get_test_task, (5,)),
            (another_task, (5, 9, 2)),
            (get_test_task, (3,)),
            (another_task, (3, 0, 1)),
        ],
        4
    )
    time.sleep(1)
    (process_controller.wait_count())
    (process_controller.alive_count())
    time.sleep(2)
    (process_controller.wait_count())
    (process_controller.alive_count())
    process_controller.wait()



if __name__ == "__main__":
    main()