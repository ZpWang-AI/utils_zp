## copy this sh file, use ". bashrc_zp.sh" to import it

export PS1='\[\e[1;32m\][\u@\h \w]$ \[\e[0m\]'  # make the prompt string green
# add \[\e[XXX\] to change the font color

export HF_ENDPOINT="https://hf-mirror.com"

# alias psa="ps -aux"
alias psa="ps -aux | grep -v grep"
alias ls="ls --color=auto"
alias condaa="conda activate"
alias condada="conda deactivate"
alias listusage="du -h -d 1 | sort -hr"
alias kkgpu="watch --color -n1 gpustat -cpu --color"

## source ~/.bashrc
