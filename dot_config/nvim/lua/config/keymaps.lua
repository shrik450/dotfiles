-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

local function relpath_from_root()
  local path = vim.api.nvim_buf_get_name(0)
  if path == "" then
    return nil, false
  end
  local root = LazyVim.root()
  local rel = vim.fs.relpath(root, path)
  if rel then
    return rel, false
  end
  return path, true
end

local function yank(text, outside)
  vim.fn.setreg("+", text)
  vim.notify(text .. (outside and " (outside root)" or ""), vim.log.levels.INFO, { title = "Yanked" })
end

vim.keymap.set("n", "<leader>fy", function()
  local rel, outside = relpath_from_root()
  if not rel then
    return
  end
  yank(rel, outside)
end, { desc = "Copy relpath" })

vim.keymap.set("n", "<leader>fY", function()
  local rel, outside = relpath_from_root()
  if not rel then
    return
  end
  yank(rel .. ":" .. vim.api.nvim_win_get_cursor(0)[1], outside)
end, { desc = "Copy relpath:line" })

vim.keymap.set("x", "<leader>fY", function()
  local rel, outside = relpath_from_root()
  if not rel then
    return
  end
  vim.cmd('execute "normal! \\<Esc>"')
  local s = vim.fn.getpos("'<")[2]
  local e = vim.fn.getpos("'>")[2]
  local suffix = s == e and (":" .. s) or (":" .. s .. "-" .. e)
  yank(rel .. suffix, outside)
end, { desc = "Copy relpath:line" })

local function symbol_at_cursor()
  local params = vim.lsp.util.make_position_params(0, "utf-8")
  local results = vim.lsp.buf_request_sync(0, "textDocument/prepareCallHierarchy", params, 500)
  if results then
    for _, res in pairs(results) do
      if res.result and res.result[1] and res.result[1].name and res.result[1].name ~= "" then
        return res.result[1].name
      end
    end
  end
  local cword = vim.fn.expand("<cword>")
  return cword ~= "" and cword or nil
end

vim.keymap.set("n", "<leader>cy", function()
  local rel, outside = relpath_from_root()
  if not rel then
    return
  end
  local sym = symbol_at_cursor()
  if not sym then
    vim.notify("No symbol under cursor", vim.log.levels.WARN, { title = "Yank" })
    return
  end
  local line = vim.api.nvim_win_get_cursor(0)[1]
  yank(rel .. "#" .. sym .. ":" .. line, outside)
end, { desc = "Copy relpath#symbol:line" })
