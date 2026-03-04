return {
  {
    "NeogitOrg/neogit",
    dependencies = { "nvim-lua/plenary.nvim" },
    cmd = "Neogit",
    keys = {
      { "<leader>gn", "<cmd>Neogit<cr>", desc = "Neogit status" },
    },
    opts = {
      kind = "tab",
    },
  },
  {
    "barrettruth/diffs.nvim",
    init = function()
      vim.g.diffs = {
        fugitive = true,
        neogit = true,
      }
    end,
  },
}
