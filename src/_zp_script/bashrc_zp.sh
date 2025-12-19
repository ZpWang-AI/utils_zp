## copy this sh file, use ". bashrc_zp.sh" to import it

export PS1='\[\e[1;32m\][\u@\h \w]$ \[\e[0m\]'  # make the prompt string green
# add \[\e[XXX\] to change the font color

export HF_ENDPOINT="https://hf-mirror.com"

# alias psa="ps -aux"
alias psa="ps -aux | grep -v grep"
alias psaa="ps -aux | grep -v grep | grep -v .vscode-server | grep -v /code-server/ | grep -v gpustat | grep -v 'ps -aux'"
# alias pszp="ps -aux | grep -v grep | grep -v .vscode-server | grep -v /code-server/ | grep -v /gpustat | grep zp | grep -v 'ps -aux'"

alias ls="ls --color=auto"
alias condaa="conda activate"
alias condada="conda deactivate"
alias lsize="du -h -d 1 | sort -hr"
alias ldisk="df -h | grep -v /run/user/"
alias kkgpu="watch --color -n1 gpustat -cpu --color"
alias sourcebashrc="source ~/.bashrc"

## source ~/.bashrc

# =====================================================
# Stack Size
ulimit -s 32768

# =====================================================
# tmux
alias tmuxs="tmux new -s"
alias tmuxa="tmux attach -t"
alias tmuxk="tmux kill-session -t"
alias tmuxls="tmux ls"
alias tmuxrename="tmux rename-session -t"

# =====================================================
# screen
alias scs="screen -S"
alias scr="screen -r"
alias sck="screen -k"
alias scls="screen -ls"
screname() {
    OLD_NAME="$1"
    NEW_NAME="$2"
    screen -S "${OLD_NAME}" -X sessionname "${NEW_NAME}"
}
alias echosty="echo $STY"

# =====================================================
# git
alias gitr="git remote"
alias gitra="git remote add"
