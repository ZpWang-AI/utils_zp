# 查看端口
netstat -tunlp | grep [port]
lsof -t -i:[port]

ssh-keygen -t rsa -C "your_email@example.com"