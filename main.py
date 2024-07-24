from contextlib import ExitStack
import multiprocessing as mp
from queue import Queue
import threading
import time


class ProcessController:
    def __init__(self):
        self.max_process_number = None
        self.wait_counter = None
        self.task_queue = None
        self.publisher = None

    def set_max_proc(self, process_number):
        self.max_process_number = process_number

    def start(self, tasks, max_exec_time):
        if self.max_process_number is None:
            raise Exception("First, set max process number by set_max_proc()")

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
        # TODO proper private methods
        for task in tasks:
            task_queue.put(True)
            runner = threading.Thread(
                target=self.runner,
                args=(task_queue, task_exec_time, task)
            )
            self.wait_counter -= 1
            runner.start()

        task_queue.join()

    @staticmethod
    def runner(task_queue, max_exec_time, task):
        with ExitStack() as stack:
            @stack.callback
            def complete_task():
                task_queue.get()
                task_queue.task_done()

            func, args = task
            task_process = mp.Process(target=func, args=args)
            task_process.start()
            task_process.join(max_exec_time)

            task_process.terminate()
            while task_process.is_alive():
                time.sleep(0.1)

            task_process.close()
