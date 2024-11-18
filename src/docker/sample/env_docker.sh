# build env image
sudo docker build -f docker/dockerfile.env -t tsqb:env .

# # save/load image
# sudo docker save -o tsqb_image_env.tar tsqb_frontend_image:env
# sudo docker load -i tsqb_image_env.tar
