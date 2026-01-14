du -h -d 1 | sort -hr

ps -aux | grep -v grep

watch --color -n1 gpustat -cpu --color

chmod 700 .
chmod -R 700 .  # recursively chmod


# check port
netstat -tunlp | grep [port]
lsof -t -i:[port]

ssh-keygen -t rsa -C "your_email@example.com"


# zip
7z a -mx=9 exp_space.7z exp_space
zip -r a.zip ./a
