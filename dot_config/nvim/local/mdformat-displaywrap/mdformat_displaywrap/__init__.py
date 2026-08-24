"""Wrap Markdown by the width a reader sees.

mdformat counts a link as the whole `[text](url)` string when it wraps a
paragraph. An editor that conceals link targets shows only `text`, so a
line that fits on screen still gets wrapped. This plugin makes mdformat
measure a link as its link text.

How it works: the link renderer returns a placeholder as long as the link
text and stores the real link. mdformat wraps the paragraph, measuring the
placeholder. A postprocessor on the root node then puts the real links back.

Each placeholder carries its own index, because plugins are free to render
the same node more than once. Position alone is not a safe key.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, MutableMapping

from mdformat.renderer import DEFAULT_RENDERERS, WRAP_POINT

if TYPE_CHECKING:
    from markdown_it import MarkdownIt

    from mdformat.renderer import RenderContext, RenderTreeNode

__version__ = "0.1.1"

# The plugin changes line breaks only, so the parsed document stays the same.
CHANGES_AST = False

# A placeholder is a START character, then PAD characters, then the index
# of the link in base len(_DIGITS). None of these characters may be a null
# byte or whitespace: mdformat uses null bytes for its own wrap markers,
# and whitespace would let a line break fall inside a link.
_START = "\x0f"
_PAD = "\x0e"
_DIGITS = "\x01\x02\x03\x04\x05\x06\x07\x08\x10\x11\x12\x13\x14\x15\x16\x17"
_PLACEHOLDER_RE = re.compile(f"{_START}{_PAD}*[{_DIGITS}]+")

_ENV_KEY = "displaywrap_links"

_default_link = DEFAULT_RENDERERS["link"]


def _encode(index: int) -> str:
    base = len(_DIGITS)
    digits = _DIGITS[index % base]
    index //= base
    while index:
        digits = _DIGITS[index % base] + digits
        index //= base
    return digits


def _decode(digits: str) -> int:
    index = 0
    for digit in digits:
        index = index * len(_DIGITS) + _DIGITS.index(digit)
    return index


def _stored_links(env: MutableMapping[str, Any]) -> list[str]:
    return env.setdefault(_ENV_KEY, [])


def _in_paragraph(node: RenderTreeNode) -> bool:
    while node.parent:
        if node.parent.type == "paragraph":
            return True
        node = node.parent
    return False


def _link(node: RenderTreeNode, context: RenderContext) -> str:
    rendered = _default_link(node, context)

    # Only paragraphs wrap. Leave table cells and headings alone, because
    # other plugins measure those strings to align columns.
    if not context.do_wrap or not _in_paragraph(node):
        return rendered

    # Render the children a second time to get the link text on its own.
    # The text renderer only escapes characters, so a repeat render is safe.
    display = "".join(child.render(context) for child in node.children)
    display = display.replace(WRAP_POINT, " ")

    links = _stored_links(context.env)
    digits = _encode(len(links))
    placeholder = _START + _PAD * max(0, len(display) - 1 - len(digits)) + digits
    if len(placeholder) >= len(rendered):
        return rendered

    links.append(rendered)
    return placeholder


def _restore_links(text: str, node: RenderTreeNode, context: RenderContext) -> str:
    links = _stored_links(context.env)
    if not links:
        return text

    def replace(match: re.Match) -> str:
        return links[_decode(match.group().lstrip(_START + _PAD))]

    return _PLACEHOLDER_RE.sub(replace, text)


def update_mdit(mdit: MarkdownIt) -> None:
    """Leave the parser as it is. This plugin only changes rendering."""


RENDERERS = {"link": _link}
POSTPROCESSORS = {"root": _restore_links}
