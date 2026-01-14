# <<< docker 常用命令全集 >>>

# 操作前先进入项目目录 !_!
cd /home/user/test/TSQB_System

# ==================================================
# 创建和移动"环境 image"

# show image
sudo docker images

# rm image
sudo docker rmi XXX
# e.g.
sudo docker rmi 9b9cb95443b5

# rm all <none>:<none> images
docker images -f "dangling=true" -q | xargs -r sudo docker rmi

# build env image
sudo docker build -f docker/dockerfile.env -t tsqb_frontend_image:env .

# save/load image
sudo docker save -o tsqb_image_env.tar tsqb_frontend_image:env
sudo docker load -i tsqb_image_env.tar

# ==================================================
# 创建"运行 image"，运行 container

# build torun image
sudo docker build -f docker/dockerfile -t tsqb_frontend_image:latest .

# get container running
sudo docker run -v XXX:/TSQB_System/database -v XXX:/TSQB_System/prompts -d --name tsqb_frontend -p XXX:8601 tsqb_frontend_image:latest
# e.g.
sudo docker run -v /home/user/test/scenario_data/database:/TSQB_System/database -v /home/user/test/scenario_data/prompts:/TSQB_System/prompts -d --name tsqb_frontend -p 8602:8601 tsqb_frontend_image:latest

# ==================================================
# container 查看，停止，查看输出

# show containers
sudo docker ps -a 

# kill container
sudo docker rm XXX
# e.g. 
sudo docker rm ea1e84734177

# kill all exited containers
sudo docker ps -a -q --filter "status=exited" | xargs -r sudo docker rm

# watch log
sudo docker logs -f tsqb_frontend
