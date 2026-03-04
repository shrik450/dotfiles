function brewsync --description 'Dump Homebrew deps to Brewfile and sync to chezmoi'
    brew bundle dump --file=~/.config/brew/Brewfile --force --no-vscode --no-go --no-cargo --no-uv
    and chezmoi add ~/.config/brew/Brewfile
end
