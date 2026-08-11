if status is-interactive
    # Commands to run in interactive sessions can go here
    atuin init fish | source

    starship init fish | source

    zoxide init fish | source

    mise activate fish | source

    fish_add_path "~/.local/bin"
end

# Added by LM Studio CLI (lms)
set -gx PATH $PATH /Users/shrik450/.lmstudio/bin
# End of LM Studio CLI section


# pnpm
set -gx PNPM_HOME "/Users/shrik450/Library/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end
