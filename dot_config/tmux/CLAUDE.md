# Tmux Configuration Project

## Goal

Set up tmux as the primary terminal multiplexer for a workflow migrating from
iTerm2 to Ghostty. Ghostty has limitations with tabbing and scrollback search,
so tmux will handle tabs, scrollback, and session management.

## User Environment

- **Terminal**: Ghostty (migrating from iTerm2)
- **Shell**: fish (login shell is zsh, interactive shell is fish)
- **Editor**: nvim 0.11.6
- **tmux**: 3.6a
- **macOS** (Darwin 24.6.0, Apple Silicon)
- **Window Manager**: PaperWM.spoon (tiling, similar to niri/PaperWM)
- **fzf**: 0.67.0 (installed via Homebrew)
- **Claude Code**: Used heavily, multiple instances per project
- **TPM**: Not installed yet
- **Ghostty**: `macos-option-as-alt = left` already set

## Workflow Requirements

1. **Tab-centric**: No panes. Multiple named tabs (tmux windows) per session.
2. **Typical project session**: 1-3 Claude Code tabs, 1+ command tabs, maybe
   a test/background process tab.
3. **Claude Code compatibility**: Keybindings must not clash with CC.
4. **Separate nvim window**: nvim runs in a different OS window managed by
   PaperWM.spoon. Would like convenience features to open files from CC/test
   output in nvim.
5. **Smooth on-ramp**: Config should be approachable, not overwhelming.

## Design Decisions (Finalized)

- **Prefix key**: `Ctrl+Space`
- **Tab switching**: `Alt+H` / `Alt+L` (prev/next, no number switching)
- **Status bar**: Powerline-style, GitHub Dark color palette
- **Persistence**: Deferred (tmux-continuum planned for later)
- **Fuzzy tab switch**: `prefix+f` with fzf popup
- **Copy mode**: vi-style (hjkl nav, / search, v select, y yank)
- **nvim integration**: `e` script using `nvim --server --remote`
- **Auto-start**: No — start tmux manually
- **No panes**: Config won't set up pane bindings

## Ghostty Keybindings (relevant)

- `Cmd+T` = new tab (Ghostty tab, not tmux — irrelevant once in tmux)
- `Cmd+1..9` = goto tab (Ghostty level)
- `Cmd+Shift+[/]` = prev/next tab (Ghostty level)
- `Ctrl+Tab` / `Ctrl+Shift+Tab` = next/prev tab (Ghostty level)
- `Cmd+W` = close surface
- `Cmd+N` = new window
- `Cmd+K` = clear screen
- `Cmd+Shift+J` = write screen to paste
- `Cmd+Enter` = fullscreen

## tmux.conf Keybinding Reference

| Binding | Action |
|---|---|
| `Ctrl+Space` | Prefix |
| `Alt+H` | Previous tab |
| `Alt+L` | Next tab |
| `prefix + c` | New tab (inherits cwd) |
| `prefix + ,` | Rename tab |
| `prefix + x` | Close tab (with confirm) |
| `prefix + f` | fzf fuzzy tab switch |
| `prefix + /` | Enter copy mode + search (one step) |
| `prefix + [` | Enter copy mode (scrollback) |
| `prefix + F` | fzf fuzzy search over scrollback |
| `prefix + o` | fzf picker for URLs and file paths on screen |
| `prefix + r` | Reload config |
| `prefix + s` | Session switcher (built-in) |
| `?` (in copy mode) | Search backward (toward older output) |
| `/` (in copy mode) | Search forward (toward newer output) |
| `v` (in copy mode) | Begin selection |
| `V` (in copy mode) | Select line |
| `y` (in copy mode) | Yank to system clipboard |
| `q` / `Escape` (in copy mode) | Exit copy mode |
