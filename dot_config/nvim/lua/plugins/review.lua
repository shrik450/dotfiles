return {
  {
    "NeogitOrg/neogit",
    dependencies = { "nvim-lua/plenary.nvim" },
    cmd = "Neogit",
    keys = {
      { "<leader>gn", "<cmd>Neogit<cr>", desc = "Neogit status" },
    },
    opts = {
      kind = "replace",
    },
  },
  {
    "barrettruth/diffs.nvim",
    init = function()
      vim.g.diffs = {
        integrations = {
          fugitive = true,
          neogit = true,
        },
        highlights = {
          intra = {
            enabled = false,
          },
        },
      }
    end,
  },
}
