# -*- coding: utf-8 -*-
# autostart = true

from xkeysnail.transform import *

terminals = [
    "gnome-terminal",
    "konsole",
    "kitty",
    # Not strictly a terminal, but requires C and M to be normal.
    "emacs-gtk",
    "emacs",
    # This doesn't work.
    # "barrier", # Because I want to send raw events across instead
]
terminals = [term.casefold() for term in terminals]

define_modmap(
    {
        Key.CAPSLOCK: Key.ESC,
    }
)

define_conditional_modmap(
    lambda wm_class: wm_class.casefold() not in terminals,
    {
        Key.LEFT_CTRL: Key.LEFT_ALT,
        Key.LEFT_ALT: Key.LEFT_CTRL,
    }
)

define_keymap(
    lambda wm_class: wm_class.casefold() not in terminals,
    {
        K("C-Shift-left_brace"): K("C-page_up"),
        K("C-Shift-right_brace"): K("C-page_down"),
        K("C-Space"): K("M-Space"),
    }
)
