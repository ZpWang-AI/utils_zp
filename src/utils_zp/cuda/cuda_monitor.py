import threading

from .utils_cuda import *
from ..file_io import json_dump, json_load


class CUDAMemoryMonitor:
    def __init__(self, cuda_ids:List[int], save_filepath, monitor_gap=3) -> None:
        self.cuda_ids = cuda_ids
        self.save_filepath = path(save_filepath)
        assert self.save_filepath.suffix == '.jsonl'
        self.monitor_gap = monitor_gap
        
        self.start_time = time.time()
        self.keep_monitor = True

        total_mem = CUDAUtils.query_cuda_memory(
            cuda_id=cuda_ids[0], target='total',
        )
        json_dump(total_mem, save_filepath)
        self.process = threading.Thread(
            target=self.monitor, daemon=True,
        )
        self.process.start()
        
    def monitor(self):
        while self.keep_monitor:
            mems = [
                CUDAUtils.query_cuda_memory(
                    cuda_id=cid, target='used'
                ) for cid in self.cuda_ids
            ]
            monitor_time = int(time.time()-self.start_time)

            json_dump([monitor_time, mems], self.save_filepath)
            
            time.sleep(self.monitor_gap)
    
    def close(self):
        self.keep_monitor = False
        self.process.join()
    
    @classmethod
    def draw_from_json(cls, save_filepath, output_filepath):
        import numpy as np
        import matplotlib.pyplot as plt
        
        saved_res = json_load(save_filepath)
        if not saved_res:
            raise Exception('wrong result')
        total_mem = saved_res.pop(0)
        x, ys = zip(saved_res)
        
        max_x = max(x)
        if max_x > 60*5:
            x = [d/60 for d in x]
        elif max_x > 3600*5:
            x = [d/3600 for d in x]
        
        ys = list(zip(*ys))
        for y in ys:
            plt.plot(x, y)
            max_id = np.argmax(y)
            plt.plot(x[max_id], y[max_id], )
        

