#!/bin/bash

# 源目录和目标目录（与正向操作保持一致）
source_dir="/root/autodl-fs/_fs_data/PhyDy_data/data/WISA-80K/encoded_video"
target_dir="/root/autodl-tmp/PhyDy_data/data/WISA-80K"

# 检查软链接是否存在
if [ ! -L "$source_dir" ]; then
    echo "错误：源位置不是软链接或不存在 - $source_dir"
    echo "请确认这是否是正向操作后的状态"
    exit 1
fi

# 获取软链接指向的实际路径
actual_path=$(readlink -f "$source_dir")
echo "检测到软链接指向: $actual_path"

# 验证实际路径是否存在
if [ ! -d "$actual_path" ]; then
    echo "错误：软链接指向的实际路径不存在 - $actual_path"
    exit 1
fi

# 确认目标路径与预期一致
expected_dir_name=$(basename "$source_dir")
expected_target_path="$target_dir/$expected_dir_name"

if [ "$actual_path" != "$expected_target_path" ]; then
    echo "警告：软链接指向的路径与预期不一致"
    echo "预期路径: $expected_target_path"
    echo "实际路径: $actual_path"
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "操作已取消"
        exit 0
    fi
fi

# 删除软链接
echo "正在删除软链接..."
rm "$source_dir"

# 移动目录回原位置
echo "正在将目录移回原位置..."
mv "$actual_path" "$(dirname "$source_dir")/"

# 验证操作
if [ -d "$source_dir" ] && [ ! -L "$source_dir" ] && [ ! -e "$actual_path" ]; then
    echo "逆向操作成功完成！"
    echo "目录已移回: $source_dir"
    echo "原目标路径已清空: $actual_path"
else
    echo "警告：某些操作可能未成功完成，请手动检查"
    echo "当前状态:"
    echo "  - $source_dir 是否存在: $(if [ -e "$source_dir" ]; then echo "是 ($(ls -ld "$source_dir" | cut -c1))"; else echo "否"; fi)"
    echo "  - $actual_path 是否存在: $(if [ -e "$actual_path" ]; then echo "是"; else echo "否"; fi)"
fi