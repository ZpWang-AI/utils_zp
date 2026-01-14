# kill all exited containers
sudo docker ps -a -q --filter "status=exited" | xargs -r sudo docker rm

# rm all <none>:<none> images
docker images -f "dangling=true" -q | xargs -r sudo docker rmi
