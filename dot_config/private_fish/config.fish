if status is-interactive
    # Commands to run in interactive sessions can go here
    atuin init fish | source

    starship init fish | source

    zoxide init fish | source

    mise activate fish | source

    fish_add_path "~/.local/bin"
end
