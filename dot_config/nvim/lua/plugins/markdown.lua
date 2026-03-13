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

        map("n", "o", "<Cmd>MDListItemBelow<CR>", opts)
        map("n", "O", "<Cmd>MDListItemAbove<CR>", opts)
        map("i", "<CR>", "<Cmd>MDListItemBelow<CR>", opts)
        map("n", "<leader>x", "<Cmd>MDTaskToggle<CR>", opts)
        map("x", "<leader>x", "<Cmd>MDTaskToggle<CR>", opts)
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
