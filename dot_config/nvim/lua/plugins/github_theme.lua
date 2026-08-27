return {
  {
    "projekt0n/github-nvim-theme",
    name = "github-theme",
    opts = {
      groups = {
        github_dark_default = {
          -- The theme paints split separators in its darkest border colour,
          -- one step off the background, so they are invisible. This is
          -- GitHub's neutral.emphasis token, which herdr uses for its borders.
          WinSeparator = { fg = "#6e7681" },
        },
      },
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "github_dark_default",
    },
  },
}
