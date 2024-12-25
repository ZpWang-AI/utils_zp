from .utils_cuda import *


class CUDABalancer:
    def __init__(
        self, 
        cuda_ids:List[int]=None, 
        rest_mem_mb:Union[int,float]=None, 
        target_mem_mb:Union[int,float]=None, 
        keep_running:bool=False, 
        refresh_gap:float=0.1, 
        wait_before_start:Union[int,float]=10
    ) -> None:
        if cuda_ids is not None:
            self.cuda_ids = cuda_ids
        else:
            self.cuda_ids = [0]
        
        if rest_mem_mb is not None:
            self.target_mem_mb = CUDAUtils.query_cuda_memory(
                cuda_id=self.cuda_ids[0], target='total',
            ) - float(rest_mem_mb)
        elif target_mem_mb is not None:
            self.target_mem_mb = float(target_mem_mb)
        else:
            raise "rest_mem_mb and target_mem_mb are all None"
        
        self.keep_balance = True
        self.keep_running = bool(keep_running)
        self.refresh_gap = float(refresh_gap)
        self.wait_before_start = float(wait_before_start) + 0.001
        
        self.run_process_list = [threading.Thread(
            target=self.run, daemon=True, kwargs={'cuda_id': cuda_id})
            for cuda_id in self.cuda_ids
        ]
        for process in self.run_process_list:
            process.start()
            
        self.balance_process = threading.Thread(
            target=self.balance, daemon=True,
        )
        self.balance_process.start()
    
    def _balance_one_cuda(self, cuda_id, tensor_stack):
        import torch
        
        def fill_tensor(e):
            return torch.arange(1, 10**e, device=f'cuda:{cuda_id}')
        {
            'e=8': 764,
            'e=7': 78, 
            'e=6': 10,
            'e=5': 1,
        }
        for pid, (e, b_mem) in enumerate(zip([7,5], [80,1])):
            try:
                while CUDAUtils.query_cuda_memory(
                    cuda_id=cuda_id, target='used'
                ) < self.target_mem_mb-b_mem:
                    new_tensor = fill_tensor(e)
                    tensor_stack[pid].append(new_tensor)
            except torch.cuda.OutOfMemoryError:
                pass
        for pid, (e, b_mem) in enumerate(zip([7,5], [78,1])):
            while tensor_stack[pid] and CUDAUtils.query_cuda_memory(
                cuda_id=cuda_id, target='used'
            ) >= self.target_mem_mb:
                tensor_stack[pid].pop()
                torch.cuda.empty_cache()

    def balance(self):
        time.sleep(self.wait_before_start)
        print('balancer starts')
        
        tensor_stacks = [
            [[], []]
            for _ in self.cuda_ids
        ]
        while self.keep_balance:
            for cuda_id, tensor_stack in zip(self.cuda_ids, tensor_stacks):
                self._balance_one_cuda(
                    cuda_id=cuda_id,
                    tensor_stack=tensor_stack,
                )
            
            time.sleep(self.refresh_gap)
    
    def run(self, cuda_id):
        import torch
        
        x = torch.eye(100, device=f'cuda:{cuda_id}')
        while self.keep_running:
            for _ in range(100):
                x *= x
            time.sleep(0.001)

    def start(self):
        self.balance()
        
    def close(self):
        self.keep_balance = False
        self.keep_running = False
        self.balance_process.join()
        for process in self.run_process_list:
            process.join()
            
        print('balancer ends')
