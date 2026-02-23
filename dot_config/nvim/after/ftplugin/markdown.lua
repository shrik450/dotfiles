vim.opt_local.comments = { "fb:*", "fb:-", "fb:+", "fb:1.", "n:>" }

vim.api.nvim_create_autocmd("BufWinEnter", {
  buffer = 0,
  once = true,
  callback = function()
    vim.bo.indentexpr = ""
  end,
})
