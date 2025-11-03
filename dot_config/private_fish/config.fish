if status is-interactive
    # Commands to run in interactive sessions can go here
end

starship init fish | source

zoxide init fish | source

mise activate fish | source

fish_add_path "~/.local/bin"

# Added by LM Studio CLI (lms)
set -gx PATH $PATH /Users/shrik450/.lmstudio/bin
# End of LM Studio CLI section

