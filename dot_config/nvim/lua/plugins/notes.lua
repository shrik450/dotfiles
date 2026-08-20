local dir = vim.fn.stdpath("config") .. "/local/notes.nvim"
return {
  {
    dir = dir,
    name = "notes.nvim",
    ft = "markdown",
    opts = {},
    enabled = function()
      return (vim.uv or vim.loop).fs_stat(dir) ~= nil
    end,
  },
}
