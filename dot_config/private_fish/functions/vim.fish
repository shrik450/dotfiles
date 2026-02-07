function vim --wraps=nvim --description 'nvim with per-project server socket'
    set -l project (basename (git rev-parse --show-toplevel 2>/dev/null; or echo $PWD))
    set -l sock /tmp/nvim-$project.sock
    nvim --listen $sock $argv
end
