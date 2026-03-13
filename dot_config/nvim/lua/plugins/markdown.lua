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

        local function on_list(line)
          return line:match("^%s*[-*+]%s") or line:match("^%s*%d+[.)]%s")
        end

        map("n", "o", function()
          if on_list(vim.api.nvim_get_current_line()) then
            vim.cmd("MDListItemBelow")
          else
            local key = vim.api.nvim_replace_termcodes("o", true, false, true)
            vim.api.nvim_feedkeys(key, "n", false)
          end
        end, opts)

        map("n", "O", function()
          if on_list(vim.api.nvim_get_current_line()) then
            vim.cmd("MDListItemAbove")
          else
            local key = vim.api.nvim_replace_termcodes("O", true, false, true)
            vim.api.nvim_feedkeys(key, "n", false)
          end
        end, opts)

        map("i", "<CR>", function()
          if on_list(vim.api.nvim_get_current_line()) then
            vim.cmd("MDListItemBelow")
          else
            local cr = vim.api.nvim_replace_termcodes("<CR>", true, false, true)
            vim.api.nvim_feedkeys(cr, "n", false)
          end
        end, opts)

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
