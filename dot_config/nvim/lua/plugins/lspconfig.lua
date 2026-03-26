return {
  "neovim/nvim-lspconfig",
  opts = {
    inlay_hints = { enabled = false },
    servers = {
      basedpyright = {
        root_dir = function(fname)
          local util = require("lspconfig.util")
          return util.find_git_ancestor(fname) or util.root_pattern("pyproject.toml")(fname)
        end,
      },
    },
  },
}
