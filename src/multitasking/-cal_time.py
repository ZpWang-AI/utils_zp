from threading_ import run_multitasks
# from asyncio_ import run_multitasks
# from utils_zp.multitasking._threading import run_multitasks
from utils_zp import BaseDecoratorCreator
import time
import asyncio


def task_io(p):
    # asyncio.sleep(3)
    time.sleep(3)
    # print(p)
    return -p


def task_cpu():
    i = 1
    for d in range(10000000):
        i *= d
    return 


@BaseDecoratorCreator(
    print_info=True,
    print_running_time=True,
)
def main(func, repeat_times) -> None:
    tasks = [(func, (p,), {})for p in range(repeat_times)]
    res = run_multitasks(tasks)
    print(repeat_times)
    # print(res)


if __name__ == '__main__':
    main(task_cpu, 5)
    # main(task_io, 5)
