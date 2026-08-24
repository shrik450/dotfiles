# mdformat-displaywrap

An mdformat plugin that wraps paragraphs by the width a reader sees.

mdformat counts a link as the whole `[text](url)` string. Neovim conceals the
target, so it shows only `text`. A line that looks short on screen still gets
wrapped. This plugin makes mdformat measure a link as its link text.

## Scope

The plugin changes inline links inside paragraphs only. It leaves headings,
table cells, autolinks, and images as mdformat renders them. Table alignment
stays byte-identical to plain mdformat.

The measured width is the length of the rendered link text. Markup inside the
text, such as the `**` in `[**bold**](url)`, counts toward that length.

## Use

Pass the directory to uvx:

```
uvx --with /path/to/mdformat-displaywrap mdformat --wrap 80 file.md
```

`nvim/lua/plugins/markdown.lua` already does this through conform.

## After you edit the plugin

uv caches the built wheel by version. Bump `version` in `pyproject.toml` after
you change the code, or uvx keeps running the old build.
