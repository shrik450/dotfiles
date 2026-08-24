return {
  {
    "projekt0n/github-nvim-theme",
    name = "github-theme",
    opts = {
      groups = {
        github_dark_default = {
          -- The theme paints split separators in its darkest border colour,
          -- one step off the background, so they are invisible. Use the
          -- border colour GitHub's own dark UI uses.
          WinSeparator = { fg = "#30363d" },
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
