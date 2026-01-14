root_dir="/home/ScenarioSystem_frontend"
python_exe="/root/anaconda3/envs/zp_main/bin/python"
main_file="${root_dir}/src/main_v3_4_0.py"
port="8793"

ps -aux | grep $main_file | grep -v grep

count=$(ps -aux | grep $main_file | grep -v grep | wc -l)
echo "===================================================="

if [ $count -ge 1 ]; then
    echo "Stop the old one to start a new one"
    kill $(ps -aux | grep $main_file | grep -v grep | awk '{print $2}')
else
    echo "No old process found"
fi

pid=$(lsof -t -i:$port)
if [ -n "$pid" ]; then
    kill -9 $pid
    echo "Port ${port} is occupied. PID ${pid} is killed to release it."
else
    echo "Port ${port} is available."
fi

nohup $python_exe $main_file --port ${port} > "${root_dir}/logs/log.v2.out" 2>&1 &
echo "start running"
echo "===================================================="
ps -aux | grep $main_file | grep -v grep
