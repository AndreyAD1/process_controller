from contextlib import ExitStack
import multiprocessing as mp
from queue import Queue
import threading
import time


class ProcessController:
    """ProcessController runs the functions concurrently.

    For example:
        pc = ProcessController()
        pc.set_max_proc(2)
        pc.start(
            [
                (func1, (1, 2)),
                (func2, (3,)),
                (func3, tuple()),
            ],
            5
        )
        pc.wait()
    """

    def __init__(self):
        self.max_process_number = None
        self.wait_counter = None
        self.task_queue = None
        self.dispatcher = None

    def set_max_proc(self, process_number):
        self.max_process_number = process_number

    def start(self, tasks, max_exec_time):
        if self.max_process_number is None:
            raise ProcessControllerException(
                "You should call set_max_proc() first"
            )

        self.task_queue = Queue(maxsize=self.max_process_number)
        self.wait_counter = len(tasks)
        dispatcher = threading.Thread(
            target=self.__run_dispatcher,
            args=(self.task_queue, max_exec_time, tasks),
            daemon=True
        )
        self.dispatcher = dispatcher
        dispatcher.start()

    def wait(self):
        if self.dispatcher is None:
            raise ProcessControllerException("You should call start() first")

        self.dispatcher.join()

    def alive_count(self):
        if self.task_queue is None:
            raise ProcessControllerException("You should call start() first")

        return self.task_queue.qsize()

    def wait_count(self):
        if self.wait_counter is None:
            raise ProcessControllerException("You should call start() first")
        return self.wait_counter

    def __run_dispatcher(self, task_queue, task_exec_time, tasks):
        for task in tasks:
            task_queue.put(True)
            runner = threading.Thread(
                target=self.__runner,
                args=(task_queue, task_exec_time, task)
            )
            self.wait_counter -= 1
            runner.start()

        task_queue.join()

    @staticmethod
    def __runner(task_queue, max_exec_time, task):
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


class ProcessControllerException(Exception):
    pass
