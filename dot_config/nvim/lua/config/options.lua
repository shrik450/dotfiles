-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

vim.g.root_spec = { { ".git" }, "cwd" }

vim.g.lazyvim_python_lsp = "basedpyright"

-- Over SSH (e.g., inside herdr/ghostty), LazyVim clears `clipboard` so that
-- OSC 52 can be used, but nvim's auto-detection of OSC 52 does not see the
-- feature through herdr's emulated terminal, so no provider attaches and yanks
-- go nowhere. Force the built-in OSC 52 provider so yanks/pastes reach the
-- host clipboard. On localhost, LazyVim already handles this correctly, so
-- leave it alone.
if vim.env.SSH_CONNECTION then
  vim.opt.clipboard = "unnamedplus"
  vim.g.clipboard = "osc52"
end