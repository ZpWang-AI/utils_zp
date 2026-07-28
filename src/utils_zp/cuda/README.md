# CUDA Module

`utils_zp.cuda` 现在按职责拆成了 5 个模块，其中 `idle_burn.py` 更偏实验和压力测试。

## Public API

### `query.py`

负责查询 GPU 基础信息。

常用接口：

- `list_gpu_indices()`
- `list_gpus()`
- `get_gpu(index)`
- `GPUInfo`

适合做：

- 查看所有卡
- 拿单卡显存信息
- 获取 GPU 名称、UUID、温度、利用率

### `select.py`

负责选卡和设置 `CUDA_VISIBLE_DEVICES`。

常用接口：

- `get_available_gpus()`
- `pick_gpu_indices()`
- `wait_for_available_gpus()`
- `set_cuda_visible_devices()`
- `auto_set_cuda_visible()`

适合做：

- 选空闲卡
- 等待可用卡
- 自动设置环境变量

默认语义说明：

- `pick_gpu_indices(wait=False)` 在可用 GPU 数量少于 `required_count` 时会直接抛出 `ValueError`，不会静默少返回几张卡
- 如果希望等待到足量 GPU 可用，再改用 `wait=True`

### `monitor.py`

负责后台记录显存变化。

常用接口：

- `GPUMemoryMonitor`
- `load_monitor_log()`
- `plot_monitor_log()`

适合做：

- 训练过程监控
- 保存 jsonl 日志
- 事后画图排查显存变化

### `occupy.py`

负责把一张或多张卡占到目标显存附近。

其中 `GPUMemoryOccupier(device_indices=...)` 里的编号统一按 **物理 GPU 编号**
解释，也就是 `nvidia-smi` 看到的 index。模块内部会在真正创建 torch tensor
时自动映射成 torch 可见的逻辑 device，这样即使设置了
`CUDA_VISIBLE_DEVICES`，NVML 查询和 torch 分配也还是对同一张物理卡生效。

常用接口：

- `GPUMemoryOccupier`

适合做：

- 压测
- 占卡实验
- 模拟显存紧张环境

## Stress Test Module

### `idle_burn.py`

这是一个偏实验用途的压力测试模块。

现在它的定位是：

- 用 `nvidia-smi` 查询单卡利用率
- 判断目标 GPU 上是否有其他计算进程
- 构造一个简单的 torch workload
- 按不同场景把 GPU 利用率压到不同目标值附近

主要函数：

- `query_nvidia_smi_usage()`
- `list_gpu_processes()`
- `create_fp16_linear_workload()`
- `run_workload_step()`
- `stress_gpu_to_target_usage()`

`stress_gpu_to_target_usage()` 现在的核心参数是：

- `gpu_id`
- `target_usage_when_idle`
- `target_usage_when_shared`
- `calibration_step_duration_s`
- `calibration_stop_usage`
- `control_update_interval_s`

其中 `gpu_id` 统一按 **物理 GPU 编号** 解释，也就是 `nvidia-smi` 看到的 index。
函数内部会自动把它映射成 torch 可见的逻辑 device，避免 `CUDA_VISIBLE_DEVICES`
存在时 torch 编号和 `nvidia-smi` 编号不一致。

现在的控制流程分两阶段：

1. 标定阶段
- 按 `1, 2, 4, 8, ...` 这样的 QPS 梯度逐步加压
- 每档持续一小段时间
- 直到 GPU 利用率达到设定阈值，例如 `50%`
- 先测 baseline，再用这些样本估算一个粗略的 `QPS -> 增量利用率` 关系

2. 控制阶段
- 每隔固定窗口（例如 `5s`）查一次当前 GPU 利用率
- 同时判断目标 GPU 上是否有其他“显存占用超过阈值”的进程
- 根据“目标利用率 - 当前利用率”的差值，换算出 QPS 增量
- 再按更新后的目标 QPS 运行下一个控制窗口

它和 `occupy.py` 的区别是：

- `idle_burn.py` 更像临时压力测试工具
- `occupy.py` 更像正式模块

## 建议使用方式

如果只是常规开发，优先用公开接口：

```python
from utils_zp.cuda import list_gpus, pick_gpu_indices, GPUMemoryMonitor
```

如果只是做一次性实验，才考虑用：

```python
from utils_zp.cuda.idle_burn import stress_gpu_to_target_usage
```

## 环境说明

当前实现默认依赖 NVIDIA 驱动和 NVML 运行时。

如果机器上的 `libnvidia-ml` 不可用，`query.py` 相关接口会报：

```text
RuntimeError: Failed to initialize NVML ...
```

这种情况是环境问题，不是模块结构问题。
