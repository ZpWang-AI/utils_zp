from ..base_utils import *


def norm_mem_to_mb(mem):
    return int(mem) >> 20


class OneCUDA:
    def __init__(self, cuda_id, info) -> None:
        self.cuda_id:str = str(cuda_id)
        self.free:int = norm_mem_to_mb(info.free)
        self.used:int = norm_mem_to_mb(info.used)
        self.total:int = norm_mem_to_mb(info.total)
    
    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __repr__(self) -> str:
        return ', '.join([
            f'cuda: {self.cuda_id}',
            f'free: {self.free}',
            f'used: {self.used}',
            f'total: {self.total}',
        ])
        
        
class CUDAUtils:
    @staticmethod
    def query_cuda_memory(cuda_id:int, target:Literal['free', 'used', 'total']=None):
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(cuda_id)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        info = OneCUDA(cuda_id=cuda_id, info=info)
        pynvml.nvmlShutdown()
        return info if target is None else info[target]

    @staticmethod
    def get_all_cuda_id():
        import pynvml
        pynvml.nvmlInit()
        cuda_cnt = list(range(pynvml.nvmlDeviceGetCount()))
        pynvml.nvmlShutdown()
        return cuda_cnt
    
    @staticmethod
    def get_free_cudas(
        cuda_cnt=1,
        target_mem_mb=8000,
        device_range=None,
        return_str=True,
        wait_seconds=5,
        show_waiting=False,
    ):
        if not device_range:
            device_range = CUDAUtils.get_all_cuda_id()

        target_mem_mb *= 1024**2
        while 1:
            cuda_id_lst = []         
            for cuda_id in device_range:
                if CUDAUtils.query_cuda_memory(cuda_id=cuda_id, target='free') >= target_mem_mb:
                    cuda_id_lst.append(cuda_id)
                    if len(cuda_id_lst) >= cuda_cnt:
                        return ','.join(map(str,cuda_id_lst)) if return_str else cuda_id_lst
            if show_waiting:
                print('waiting cuda ...')
            time.sleep(wait_seconds)
    
    @staticmethod
    def set_cuda_visible(target_mem_mb=10000, cuda_cnt=1, device_range:List[int]=None):
        free_cuda_ids = CUDAUtils.get_free_cudas(
            target_mem_mb=target_mem_mb,
            cuda_cnt=cuda_cnt,
            return_str=True,
            device_range=device_range,
        )
        os.environ["CUDA_VISIBLE_DEVICES"] = free_cuda_ids
        print(f'=== CUDA {free_cuda_ids} ===')
        return free_cuda_ids
