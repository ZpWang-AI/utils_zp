from .base import *
from .cuda import *
from .customed import *
# from .func_plus import *
from .ml import *
from .video import *
# from .script import *

# import .plt_utils as plt_utils
# from .plt_utils imort *
from . import plt_utils



# ==================================
# tmp
# ==================================


def shut_down_autodl_server():
    os.system("/usr/bin/shutdown")

def auto_shut_down_autodl_server(inactive_minutes):
    """
    自动检测系统是否不活跃，并在满足条件时关闭服务器
    
    参数:
        inactive_minutes: 不活跃分钟数阈值
    """
    # import psutil
    
    def is_cuda_running():
        """检测CUDA上是否有运行的程序 - 最简版本"""
        try:
            import subprocess
            
            # 运行nvidia-smi获取显存使用
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode != 0:
                return False
                
            # 检查是否有显存使用超过阈值
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        if int(line.strip()) > 500:  # 500MB阈值
                            return True
                    except ValueError:
                        continue
            
            return False
            
        except Exception:
            return False
    
    def is_system_active():
        """检测系统是否活跃"""
        return is_cuda_running()
        return is_vscode_connected() or is_cuda_running()
    
    print(f"开始监控系统活动，将在 {inactive_minutes} 分钟不活跃后关闭服务器...")
    inactive_seconds = inactive_minutes * 60
    last_active_time = time.time()
    current_inactive_time = 0
    
    while True:
        try:
            if is_system_active():
                # 系统活跃，重置计时器
                last_active_time = time.time()
                current_inactive_time = 0
                print("检测到系统活动，重置计时器")
            else:
                # 系统不活跃，计算不活跃时间
                current_inactive_time = time.time() - last_active_time
                print(f"系统不活跃时间: {current_inactive_time/60:.1f} 分钟")
                
                if current_inactive_time >= inactive_seconds:
                    print(f"系统已不活跃超过 {inactive_minutes} 分钟，正在关闭服务器...")
                    shut_down_autodl_server()
                    break
            
            # 每分钟检查一次
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("监控被用户中断")
            break
        except Exception as e:
            print(f"监控过程中出现错误: {e}")
            time.sleep(5)