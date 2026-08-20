# Dotfiles

This repository holds the dotfiles that chezmoi manages. The source lives in
`~/.local/share/chezmoi`, and chezmoi writes the files into `~`.

## Package management

Every package must be in exactly one of these tiers:

| Tier   | File                         | Applies to      | Holds                                             |
| ------ | ---------------------------- | --------------- | ------------------------------------------------- |
| Shared | `.config/mise/config.toml`   | macOS and Linux | Language runtimes and command-line tools          |
| macOS  | `.config/brew/Brewfile`      | macOS           | GUI apps, fonts, and anything mise cannot install |
| Linux  | `.config/packages/linux.txt` | Linux           | The Linux equivalent of the Brewfile              |

`.chezmoiignore` hides the Brewfile on Linux and the package list on macOS.

### Add a new tool

1. Is it a GUI app, a font, or macOS only? Add it to the Brewfile as a cask.
2. Can mise install it? Run `mise registry | grep <name>` to check. If yes, add
   it to `.config/mise/config.toml`.
3. Otherwise add it to both the Brewfile and `.config/packages/linux.txt`.

### Install packages

Package installation is not part of `chezmoi apply`. Run the following commands
yourself.

Install or update the shared tools on any machine:

```sh
mise install
```

Install the macOS packages:

```sh
brew bundle --file=~/.config/brew/Brewfile
```

Uninstall macOS packages that the Brewfile no longer lists. Read the list of
packages that the command prints before you confirm:

```sh
brew bundle cleanup --file=~/.config/brew/Brewfile
```

Rewrite the Brewfile from the packages that are installed. The command
overwrites your grouping comments, so check the diff:

```sh
brew bundle dump --force --no-vscode --file=~/.config/brew/Brewfile
```

Install the Linux packages on Debian or Ubuntu:

```sh
sudo apt install $(grep -v '^#' ~/.config/packages/linux.txt | grep -v '^$')
```

Install mise from its official repository first, because `apt` does not include
it. See [Install mise with apt](https://mise.jdx.dev/installing-mise.html#apt).

## Manage files with chezmoi

Show what would change:

```sh
chezmoi diff
chezmoi status
```

Write the changes to your home directory:

```sh
chezmoi apply
```

Copy a file you edited in place back into the source:

```sh
chezmoi re-add ~/.config/some/file
```

Start tracking a new file:

```sh
chezmoi add ~/.config/some/file
```

## Machine settings

`.chezmoi.toml.tmpl` asks two questions the first time you run `chezmoi init` on
a machine. The command writes the answers to `~/.config/chezmoi/chezmoi.toml`.

| Setting         | Default                        | Effect                                                         |
| --------------- | ------------------------------ | -------------------------------------------------------------- |
| `work`          | `true` on the AllSpice MacBook | Sign commits with the 1Password SSH key and use the work email |
| `personalEmail` | `shrik450@gmail.com`           | The Git email on machines where `work` is `false`              |

To change an answer, edit `~/.config/chezmoi/chezmoi.toml` and run
`chezmoi apply`.

## Externals

`.chezmoiexternal.toml.tmpl` downloads PaperWM.spoon for Hammerspoon on macOS.
The file pins it to a specific commit. To update it, change the commit and run
`chezmoi apply --refresh-externals`.
