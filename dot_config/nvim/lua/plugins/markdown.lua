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
        link_follow = false,
      },
      on_attach = function(bufnr)
        local map = vim.keymap.set
        local opts = { buffer = bufnr }

        local function in_list()
          local node = vim.treesitter.get_node()
          while node do
            if node:type() == "list_item" then
              return true
            end
            node = node:parent()
          end
          return false
        end

        local function heading_level()
          local node = vim.treesitter.get_node()
          while node do
            if node:type():match("^atx_heading") then
              local text = vim.treesitter.get_node_text(node, bufnr)
              local hashes = text:match("^(#+)")
              return hashes and #hashes or 1
            end
            node = node:parent()
          end
          return 1
        end

        local function insert_heading()
          local level = heading_level()
          local prefix = string.rep("#", level) .. " "
          local row = vim.api.nvim_win_get_cursor(0)[1]
          vim.api.nvim_buf_set_lines(bufnr, row, row, false, { "", prefix })
          vim.api.nvim_win_set_cursor(0, { row + 2, #prefix })
          vim.cmd("startinsert!")
        end

        map("i", "<M-CR>", function()
          if in_list() then
            vim.cmd("MDListItemBelow")
          else
            insert_heading()
          end
        end, opts)

        map("n", "<M-CR>", function()
          if in_list() then
            vim.cmd("MDListItemBelow")
          else
            insert_heading()
          end
        end, opts)

        local function list_marker()
          local node = vim.treesitter.get_node()
          while node do
            if node:type() == "list_item" then
              local text = vim.treesitter.get_node_text(node, bufnr)
              if text:match("^%d+[.)]") then
                return "1. "
              end
              local marker = text:match("^([%-%*%+]) ")
              if marker then
                return marker .. " "
              end
            end
            node = node:parent()
          end
          return "- "
        end

        local function insert_todo()
          local row = vim.api.nvim_win_get_cursor(0)[1]
          local prefix = list_marker() .. "[ ] "
          vim.api.nvim_buf_set_lines(bufnr, row, row, false, { prefix })
          vim.api.nvim_win_set_cursor(0, { row + 1, #prefix })
          vim.cmd("startinsert!")
        end

        map("i", "<M-S-CR>", insert_todo, opts)
        map("n", "<M-S-CR>", insert_todo, opts)

        map("n", "<leader>m", "<Cmd>MDTaskToggle<CR>", opts)
        map("x", "<leader>m", "<Cmd>MDTaskToggle<CR>", opts)

        map("n", "<leader>a", function()
          local fzf = require("fzf-lua")
          local notes_dir = vim.fn.fnamemodify(vim.api.nvim_buf_get_name(bufnr), ":p:h")
          while notes_dir ~= "/" do
            if vim.fn.isdirectory(notes_dir .. "/notes") == 1 then
              break
            end
            notes_dir = vim.fn.fnamemodify(notes_dir, ":h")
          end

          local sep = "\t"
          local entries = {}

          local clipboard = vim.fn.getreg("+")
          if clipboard:match("^https?://") then
            table.insert(entries, "url" .. sep .. clipboard .. sep .. sep .. "[clipboard] " .. clipboard)
          end

          local dirs = { notes_dir .. "/notes", notes_dir .. "/inbox" }
          for _, dir in ipairs(dirs) do
            local files = vim.fn.glob(dir .. "/*.md", false, true)
            for _, file in ipairs(files) do
              local rel = file:sub(#notes_dir + 2)
              local file_lines = vim.fn.readfile(file, "", 10)
              local title = rel
              for _, l in ipairs(file_lines) do
                local t = l:match("^title:%s*(.+)")
                if t then
                  title = t
                  break
                end
              end

              table.insert(entries, "note" .. sep .. rel .. sep .. title .. sep .. rel .. "  " .. title)

              for _, l in ipairs(vim.fn.readfile(file)) do
                local hashes, heading = l:match("^(#{1,6})%s+(.+)")
                if hashes then
                  local slug = heading:lower():gsub("[^%w%s-]", ""):gsub("%s+", "-")
                  local indent = string.rep("  ", #hashes)
                  table.insert(
                    entries,
                    "heading" .. sep .. rel .. "#" .. slug .. sep .. heading .. sep .. indent .. hashes .. " " .. heading
                  )
                end
              end
            end
          end

          local function insert_url(url)
            vim.schedule(function()
              vim.ui.input({ prompt = "Link text: " }, function(text)
                if not text or text == "" then
                  text = url
                end
                vim.api.nvim_put({ "[" .. text .. "](" .. url .. ")" }, "c", true, true)
              end)
            end)
          end

          fzf.fzf_exec(entries, {
            prompt = "Link> ",
            fzf_opts = {
              ["--delimiter"] = sep,
              ["--with-nth"] = "4",
            },
            actions = {
              ["default"] = function(selected, o)
                if not selected or #selected == 0 then
                  if o and o.last_query and o.last_query:match("^https?://") then
                    insert_url(vim.trim(o.last_query))
                  end
                  return
                end
                local parts = vim.split(selected[1], sep, { plain = true })
                local kind, path, title = parts[1], parts[2], parts[3]

                if kind == "url" then
                  insert_url(path)
                elseif kind == "note" or kind == "heading" then
                  vim.schedule(function()
                    vim.api.nvim_put({ "[" .. title .. "](" .. path .. ")" }, "c", true, true)
                  end)
                end
              end,
            },
          })
        end, opts)
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
