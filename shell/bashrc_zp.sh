## utils_zp shared shell config
## Usually this file is sourced from ~/.bashrc by running `zpbashrc`.
## Put common aliases, prompt config, and environment setup here.

# Prompt:
# - keep the path short with the last 2 levels
# - shorten the hostname to the first 6 chars to avoid very long pod names
# - use blue for both hostname and path for a compact, stable prompt
# export PROMPT_DIRTRIM=2
# export PS1='\[\033[01;34m\]\u@$(hostname | cut -c1-6)\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
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
alias sshkeygen="ssh-keygen -t rsa -b 4096 -C zhipangwang@gmail.com"

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

_zpbashrc_init_tmux() {
    if [ -n "${TMUX:-}" ] && command -v tmux >/dev/null 2>&1; then
        # Avoid keeping exited panes on screen as "dead".
        tmux set-window-option -g remain-on-exit off >/dev/null 2>&1
    fi
}
_zpbashrc_init_tmux
unset -f _zpbashrc_init_tmux

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


# =====================================================
# mlx
alias mlxw="mlx worker"
alias mlxwq="mlx worker quota"
alias mlxwl="mlx worker list"
alias mlxlogin="mlx worker login"
alias mlxwlogin="mlx worker login"


# =====================================================
# hdfs
alias hdfsd="hdfs dfs"
alias hdfss="hdfs dfs"
alias hdfsput="hdfs dfs -put"
alias hdfsget="hdfs dfs -get"
alias hdfsls="hdfs dfs -ls"
