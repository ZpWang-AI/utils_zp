start_time=$(date +%Y-%m-%d-%H-%M-%S)
out_file="/public/home/hongy/zpwang/${start_time}.occupy.log"

cmd="du -h --max-depth=1 /public/home/hongy/ | sort -rh"
nohup sh -c $cmd > $out_file 2>&1 &
