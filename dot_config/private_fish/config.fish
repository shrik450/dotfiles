if status is-interactive
    # Commands to run in interactive sessions can go here
    # Must come first: activates mise-managed tools (atuin, starship, zoxide) onto PATH
    mise activate fish | source

    atuin init fish | source

    starship init fish | source

    zoxide init fish | source

    fish_add_path "~/.local/bin"
end