from .. import __version__


def main() -> int:
    print("utils_zp")
    print(f"version: {__version__}")
    print("commands:")
    print("  zprules: 查看当前 agent 规则入口")
    print("  zpbashrc: 更新 ~/.bashrc")
    print("  zpburn: 持续占用指定 GPU 到目标利用率")
    print("  zpjobs: 查看当前 jobs 清单")
    print("  zppshell: 生成并行任务 shell")
    print("  # local cmd")
    print("  zpexp: 查看 exp/exp_versions.yaml 里标记的实验")
    print("  zpdata: 查看 data/dataset_versions.yaml 里标记的数据集")
    print("  zppremodel/zppremodels: 查看当前支持的预训练模型")
    print("  zpckpt: 查看当前支持的 checkpoint")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
