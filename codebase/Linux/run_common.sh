root_dir="/home/ScenarioSystem_frontend"
python_exe="/root/anaconda3/envs/zp_main/bin/python"
main_file="${root_dir}/src/main_v3_4_0.py"
log_dir="${root_dir}/logs"

ps -aux | grep $main_file | grep -v grep 
echo "===================================================="

count=$(ps -aux | grep $main_file | grep -v grep | wc -l)
if [ $count -ge 1 ]; then
    echo "Stop the old one to start a new one"
    kill $(ps -aux | grep $main_file | grep -v grep | awk '{print $2}')
else
    echo "No old process found"
fi

start_time=$(date +%Y-%m-%d-%H-%M-%S)
filename=$(basename "$torun_file")
filename="${filename%.*}"
nohup $python_exe $main_file > "${log_dir}/${start_time}.${filename}.log" 2>&1 &
echo "start running"
echo "===================================================="
ps -aux | grep $main_file | grep -v grep
