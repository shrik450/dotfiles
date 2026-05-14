function fj --description 'Fuzzy-jump to a directory under PWD (or given root)'
    argparse --name=fj 'd/depth=' -- $argv
    or return

    set -l depth 8
    if set -q _flag_depth
        set depth $_flag_depth
    end

    set -l root $PWD
    if set -q argv[1]
        if not test -d $argv[1]
            echo "fj: not a directory: $argv[1]" >&2
            return 1
        end
        set root (realpath $argv[1])
    end

    set -l target (
        fd --type d --hidden --exclude .git --max-depth $depth . $root \
            | fzf --reverse --height=40% \
                  --header="jump under $root (depth $depth)" \
                  --preview='ls -la {}' \
                  --preview-window=right:40%:wrap
    )

    test -n "$target"; and cd $target
end
