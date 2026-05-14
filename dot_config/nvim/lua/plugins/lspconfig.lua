return {
  "neovim/nvim-lspconfig",
  opts = {
    inlay_hints = { enabled = false },
    servers = {
      basedpyright = {
        root_dir = function(bufnr, on_dir)
          on_dir(vim.fs.root(bufnr, { ".git", "pyproject.toml" }))
        end,
      },
    },
  },
}
