return {
  {
    "tadmccorkle/markdown.nvim",
    ft = "markdown",
    opts = {
      mappings = {
        go_curr_heading = false,
        go_parent_heading = false,
        go_next_heading = false,
        go_prev_heading = false,
      },
      on_attach = function(bufnr)
        local map = vim.keymap.set
        local opts = { buffer = bufnr }

        map("i", "<M-CR>", "<Cmd>MDListItemBelow<CR>", opts)
        map("n", "<leader>m", "<Cmd>MDTaskToggle<CR>", opts)
        map("x", "<leader>m", "<Cmd>MDTaskToggle<CR>", opts)
      end,
    },
  },
  {
    "stevearc/conform.nvim",
    opts = {
      formatters_by_ft = {
        markdown = { "mdformat" },
      },
      formatters = {
        mdformat = {
          prepend_args = { "--wrap", "80" },
        },
      },
    },
  },
}
