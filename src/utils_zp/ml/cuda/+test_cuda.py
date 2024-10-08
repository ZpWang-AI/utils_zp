from utils_zp import *


def balance_monitor(cuda_ids):
    balancer = CUDABalancer(
        cuda_ids=cuda_ids,
        rest_mem_mb=10000,
        keep_running=True,
        wait_before_start=5,
    )

    monitor = CUDAMemoryMonitor(
        cuda_ids=cuda_ids,
        save_filepath=path(__file__).parent/'~cuda_usage.jsonl',
    )
    
    for i in range(20):
        print(i)
        time.sleep(1)

    # while 1:
    #     time.sleep(10)


if __name__ == '__main__':
    # balance_monitor([3])
    CUDAMemoryMonitor.draw_from_json(
        path(__file__).parent/'~cuda_usage.jsonl',
        path(__file__).parent/'~cuda_usage.png',
    )