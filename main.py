import multiprocessing as mp
import os
import time
from threading import Thread


def get_test_task(timeout):
    print(f"start to sleep {timeout} s : {os.getpid()}")
    time.sleep(timeout)
    print(f"wake up after {timeout} s : {os.getpid()}")


task_counter_lock = mp.Lock()
runner_counter_lock = mp.Lock()
MAX_TIMEOUT = 5
tasks = [
    (get_test_task, 5),
    (get_test_task, 2,),
    (get_test_task, 1,),
    (get_test_task, 3,),
    (get_test_task, 0.5,)
]
task_counter = len(tasks)
runner_counter = 0


def complete_runner(_):
    global runner_counter
    runner_counter_lock.acquire()
    runner_counter -= 1
    runner_counter_lock.release()


def runner(func, *args):
    global task_counter
    global runner_counter

    task_counter_lock.acquire()
    runner_counter_lock.acquire()
    try:
        task_thread = Thread(target=func, args=args)
        task_thread.start()
        task_counter -= 1
        runner_counter += 1
    finally:
        task_counter_lock.release()
        runner_counter_lock.release()

    task_thread.join(MAX_TIMEOUT)


def main():
    with mp.Pool(processes=3) as process_pool:
        result = process_pool.starmap_async(
            runner,
            tasks,
            callback=complete_runner,
            error_callback=complete_runner
        )
        result.get()


if __name__ == "__main__":
    main()
