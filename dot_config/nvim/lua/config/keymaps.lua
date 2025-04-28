-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

vim.keymap.set("n", "j", "gj", { desc = "Down (wrapped)" })
vim.keymap.set("n", "k", "gk", { desc = "Up (wrapped)" })

vim.keymap.set("n", "gj", "j", { desc = "Down (unwrapped)" })
vim.keymap.set("n", "gk", "k", { desc = "Up (unwrapped)" })
