import multiprocessing as mp
import os
from queue import Queue
import threading
import time


def get_test_task(timeout):
    print(f"start to sleep {timeout} s : {os.getpid()}")
    time.sleep(timeout)
    print(f"wake up after {timeout} s : {os.getpid()}")


def another_task(a, b, c):
    time.sleep(2)
    print("calculation result: ", a * b - c)


class ProcessController:
    def __init__(self):
        self.max_process_number = None
        self.wait_counter = None
        self.task_queue = None
        self.publisher = None

    def set_max_proc(self, process_number):
        self.max_process_number = process_number

    def start(self, tasks, max_exec_time):
        self.task_queue = Queue(maxsize=self.max_process_number)
        self.wait_counter = len(tasks)
        publisher = threading.Thread(
            target=self.run_publisher,
            args=(self.task_queue, max_exec_time, tasks),
            daemon=True
        )
        self.publisher = publisher
        publisher.start()

    def wait(self):
        self.publisher.join()

    def alive_count(self):
        return self.task_queue.qsize()

    def wait_count(self):
        return self.wait_counter

    def run_publisher(self, task_queue, task_exec_time, tasks):
        for task in tasks:
            task_queue.put(True)
            runner = threading.Thread(target=self.runner, args=(task_queue, task_exec_time, task))
            self.wait_counter -= 1
            runner.start()

        task_queue.join()

    def runner(self, task_queue, max_exec_time, task):
        func, args = task
        task_process = mp.Process(target=func, args=args)
        task_process.start()
        task_process.join(max_exec_time)
        task_queue.get()
        task_queue.task_done()



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
    process_controller.wait()
    # time.sleep(1)
    print(process_controller.wait_count())
    print(process_controller.alive_count())
    # time.sleep(3)
    # print(process_controller.wait_count())
    # print(process_controller.alive_count())
    # process_controller.wait()


if __name__ == "__main__":
    main()
