import os
import time
import pynvml
import threading

from typing import *
from .file_utils import dump_json, load_json


def norm_mem_to_mb(mem):
    return int(mem) >> 20

    
class GPUManager:
    @staticmethod
    def query_gpu_memory(cuda_id:int, show=True):
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(cuda_id)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        info = {
            'cuda': cuda_id,
            'free': info.free,
            'used': info.used,
            'total': info.total,
        }
        pynvml.nvmlShutdown()
        if show:
            print(*[f'{k}: {norm_mem_to_mb(v)}MB' if k !='cuda' else f'cuda: {v}'
                    for k,v in info.items()], sep=', ')
        return info

    @staticmethod
    def get_all_cuda_id():
        pynvml.nvmlInit()
        cuda_cnt = list(range(pynvml.nvmlDeviceGetCount()))
        pynvml.nvmlShutdown()
        return cuda_cnt
    
    @staticmethod
    def get_free_gpus(
        gpu_cnt=1,
        target_mem_mb=8000,
        device_range=None,
        return_str=True,
        wait_seconds=5,
        show_waiting=False,
    ):
        if not device_range:
            device_range = GPUManager.get_all_cuda_id()
            # device_range = GPUManager.get_all_cuda_id()[::-1]

        target_mem_mb *= 1024**2
        while 1:
            gpu_id_lst = []         
            for cuda_id in device_range:
                if GPUManager.query_gpu_memory(cuda_id=cuda_id, show=False)['free'] > target_mem_mb:
                    gpu_id_lst.append(cuda_id)
                    if len(gpu_id_lst) >= gpu_cnt:
                        return ','.join(map(str,gpu_id_lst)) if return_str else gpu_id_lst
            if show_waiting:
                print('waiting cuda ...')
            time.sleep(wait_seconds)
    
    @staticmethod
    def set_cuda_visible(target_mem_mb=10000, cuda_cnt=1, device_range:List[int]=None):
        free_cuda_ids = GPUManager.get_free_gpus(
            target_mem_mb=target_mem_mb,
            gpu_cnt=cuda_cnt,
            return_str=True,
            device_range=device_range,
        )
        os.environ["CUDA_VISIBLE_DEVICES"] = free_cuda_ids
        print(f'=== CUDA {free_cuda_ids} ===')
        return free_cuda_ids

    @staticmethod
    def query_gpu_mem_mb_target(cuda_id:int, target:Literal['free', 'used', 'total']):
        return norm_mem_to_mb(
            GPUManager.query_gpu_memory(cuda_id=cuda_id, show=False)[target]
        )


class GPUBalancer:
    def __init__(self, cuda_ids:List[int]=None, rest_mem_mb=None, target_mem_mb=None, keep_run=False, refresh_gap=0.1, wait_before_start=10) -> None:
        if cuda_ids is not None:
            self.cuda_ids = cuda_ids
        else:
            self.cuda_ids = [0]
        if os.environ.get('CUDA_VISIBLE_DEVICES') is None:
            self.devices = [f'cuda:{p}'for p in self.cuda_ids]
        else:
            self.devices = [f'cuda:{p}'for p in range(len(self.cuda_ids))]
        
        if rest_mem_mb is not None:
            self.target_mem_mb = GPUManager.query_gpu_mem_mb_target(
                cuda_id=self.cuda_ids[0], target='total'
            ) - rest_mem_mb
        elif target_mem_mb is not None:
            self.target_mem_mb = target_mem_mb
        else:
            raise "rest_mem_mb and target_mem_mb are all None"
        
        self.keep_balance = True
        self.keep_run = keep_run
        self.refresh_gap = refresh_gap
        self.wait_before_start = wait_before_start
        
        self.balance_process = threading.Thread(
            target=self.balance, daemon=True,
        )
        self.run_process_list = [threading.Thread(
            target=self.run, daemon=True, kwargs={'cuda_id': cuda_id, 'device':device})
            for cuda_id, device in zip(self.cuda_ids, self.devices)
        ]
        self.balance_process.start()
        for process in self.run_process_list:
            process.start()
    
    def _balance_one_gpu(self, cuda_id, device, tensor_stack):
        import torch
        def fill_tensor(e):
            return torch.arange(1, 10**e, device=device)
        {
            'e=8': 764,
            'e=7': 78, 
            'e=6': 10,
            'e=5': 1,
        }
        for e, b_mem, pid in zip([7,5], [80,1], [0,1]):
            try:
                while GPUManager.query_gpu_mem_mb_target(
                    cuda_id=cuda_id, target='used'
                ) < self.target_mem_mb-b_mem:
                    new_tensor = fill_tensor(e)
                    tensor_stack[pid].append(new_tensor)
            except torch.cuda.OutOfMemoryError:
                pass
        for e, b_mem, pid in zip([7,5], [78,1], [0,1]):
            while tensor_stack[pid] and GPUManager.query_gpu_mem_mb_target(
                cuda_id=cuda_id, target='used'
            )-b_mem >= self.target_mem_mb:
                tensor_stack[pid].pop()
                torch.cuda.empty_cache()

    def balance(self):
        time.sleep(self.wait_before_start)
        print('start balancer')
        tensor_stacks = [
            [[], []]
            for _ in self.cuda_ids
        ]
        while self.keep_balance:
            for cuda_id, device, tensor_stack in zip(self.cuda_ids, self.devices, tensor_stacks):
                self._balance_one_gpu(
                    cuda_id=cuda_id, 
                    device=device,
                    tensor_stack=tensor_stack,
                )
            
            time.sleep(self.refresh_gap)
            # GPUManager.query_gpu_memory(cuda_id=self.cuda_ids[0])
    
    def run(self, cuda_id, device):
        import torch
        import random
        x = torch.eye(100, device=device)
        while self.keep_run:
            for _ in range(100):
                x *= x
            time.sleep(0.001)
            # if random.random() < 0.1:
            #     time.sleep(self.refresh_gap)

    def close(self):
        self.keep_balance = False
        self.keep_run = False
        self.balance_process.join()
        for process in self.run_process_list:
            process.join()


class GPUMemoryMonitor:
    def __init__(self, cuda_ids:List[int], save_path, monitor_gap=3) -> None:
        self.cuda_ids = cuda_ids
        self.save_path = save_path
        self.monitor_gap = monitor_gap
        
        self.start_time = time.time()
        self.keep_monitor = True

        if cuda_ids:
            total_gpu_memory = GPUManager.query_gpu_memory(
                cuda_id=cuda_ids[0], show=False,
            )['total']
            total_gpu_memory = norm_mem_to_mb(total_gpu_memory)
            dump_json([0, total_gpu_memory], save_path, mode='a')
            self.process = threading.Thread(
                target=self.monitor, daemon=True,
            )
            self.process.start()
        
    def monitor(self):
        while self.keep_monitor:
            mems = [
                norm_mem_to_mb(
                    GPUManager.query_gpu_memory(
                        cuda_id=cid, show=False,
                    )['used']
                ) for cid in self.cuda_ids
            ]
            monitor_time = int(time.time()-self.start_time)/60

            dump_json([monitor_time, mems], self.save_path, mode='a')
            
            # self.gpu_memory.append(mem)
            # self.monitor_time.append(monitor_time)
            
            time.sleep(self.monitor_gap)
    
    def close(self):
        self.keep_monitor = False
        self.process.join()
        
    @classmethod
    def load_json_get_xy(cls, file_path) -> Tuple[List[float], List[List[int]]]:
        res = load_json(file_path)
        total_mem = res.pop(0)[1]
        if not res:
            raise Exception('wrong result')
        x = []
        ys = []
        for t, mems in res:
            x.append(t)
            ys.append(mems+[total_mem])
        ys = list(zip(*ys))
        return x, ys


if __name__ == '__main__':
    # print(GPUManager.query_gpu_memory(0))
    # print(GPUManager.get_free_gpus(target_mem_mb=2000))
    
    pass