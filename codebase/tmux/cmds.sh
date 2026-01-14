# keyboard shortcut
ctrl+b first, then cmd_key

# create
tmux 
tmux new -s xx

# leave
tmux detach
ctrl+b d

# enter
tmux attach -t xx

# show info
tmux ls
ctrl+b s

# kill
tmux kill-session -t xx

# switch
tmux switch -t xx

# rename
tmux rename-session -t xx yy
ctrl+b $


# Window & Pane
...


https://www.ruanyifeng.com/blog/2019/10/tmux.html