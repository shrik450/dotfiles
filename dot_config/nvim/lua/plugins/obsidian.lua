return {
  "obsidian-nvim/obsidian.nvim",
  version = "*",
  ft = "markdown",
  opts = {
    legacy_commands = false,
    workspaces = {
      { name = "notes", path = "~/Documents/Notes" },
    },
    completion = {
      min_chars = 2,
    },
  },
}
