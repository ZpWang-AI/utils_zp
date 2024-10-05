# 为了方便临时开发，直接 sh 此文件来完成 build image, run container 的操作
# 来自 docker_cmds.sh 第二部分
# 分割线上方的参数，人工设置路径和端口
# 分割线下方的参数，与 dockerfile 里的设置匹配，已完成调试

root_dir="/home/user/test/TSQB_System"
database_dir="/home/user/test/scenario_data/database"
prompts_dir="/home/user/test/scenario_data/prompts"
port="8501"

# ==================================================

image_name="tsqb:latest"
container_name="tsqb"
docker_filepath="docker/dockerfile"
docker_port="8601"
docker_root_dir="/usr/src/app/TSQB_System"

cd ${root_dir}

# check if the container exists, if so, remove it
container_id=$(sudo docker ps -aq --filter "name=${container_name}")
if [ -n "${container_id}" ]; then
    echo "Container ${container_name} exists, id ${container_id}, removing it..."
    sudo docker stop ${container_id}
    sudo docker rm ${container_id}
fi
# check if the image exists, if so, remove it
image_id=$(sudo docker images -q ${image_name})
if [ -n "${image_id}" ]; then
    echo "Image ${image_name} exists, id ${image_id}, removing it..."
    sudo docker rmi ${image_id}
fi
# exit 0

# build torun image
sudo docker build -f ${docker_filepath} -t ${image_name} .

# run image to get container
sudo docker run -v ${database_dir}:"${docker_root_dir}/database" -v ${prompts_dir}:"${docker_root_dir}/prompts" --name ${container_name} -p ${port}:${docker_port} -d ${image_name}

# # watch log
# sudo docker logs -f tsqb
