function vim
    set -l dir
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1
        set dir (git rev-parse --show-toplevel)
    else
        set dir $PWD
    end
    
    set -l socket "/tmp/nvim-$USER-"(echo "$dir" | md5sum | cut -d' ' -f1)
    
    if not nvim --server "$socket" --remote-send ":call foreground()<CR>" 2>/dev/null
        set -x NVIM_LISTEN_ADDRESS "$socket"
        nvim $argv
    else
        nvim --server "$socket" --remote-ui $argv
    end
end
