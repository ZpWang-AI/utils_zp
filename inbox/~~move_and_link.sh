#!/bin/bash

# 源目录和目标目录
source_dir="/root/autodl-fs/llm_zp/src/llm_zp/call_api/~tmp"
target_dir="/root/autodl-tmp/api_records"

# 检查源目录是否存在
if [ ! -d "$source_dir" ]; then
    echo "错误：源目录不存在 - $source_dir"
    exit 1
fi

# # 创建目标目录（如果不存在）
# mkdir -p "$target_dir"

# 提取源目录的名称
dir_name=$(basename "$source_dir")

# 构建目标路径
target_path="$target_dir/$dir_name"

# 检查目标路径是否已存在
if [ -e "$target_path" ]; then
    echo "错误：目标路径已存在 - $target_path"
    exit 1
fi

# 移动目录
echo "正在移动目录..."
mv "$source_dir" "$target_dir/"

# 创建软链接
echo "正在创建软链接..."
ln -s "$target_path" "$source_dir"

# 验证操作
if [ -L "$source_dir" ] && [ -d "$target_path" ]; then
    echo "操作成功完成！"
    echo "源位置: $source_dir (现在是一个软链接)"
    echo "实际位置: $target_path"
    echo "软链接目标: $(readlink -f "$source_dir")"
else
    echo "警告：某些操作可能未成功完成，请手动检查"
fi