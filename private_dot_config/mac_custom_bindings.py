# -*- coding: utf-8 -*-
# autostart = true

import re
from xkeysnail.transform import *

terminals = [
    "gnome-terminal",
    "konsole",
    "kitty",
]
terminals = [ term.casefold() for term in terminals ]

define_modmap(
    {
        Key.CAPSLOCK: Key.ESC,
    }
)

define_keymap(
    lambda wm_class: wm_class not in terminals,
    {
        K("Super-c"): K("C-c"),
        K("Super-x"): K("C-x"),
        K("Super-v"): K("C-v"),
        K("Super-z"): K("C-z"),
        K("Super-Shift-z"): K("C-Shift-z"),
        K("Super-s"): K("C-s"),
        K("Super-t"): K("C-t"),
        K("Super-w"): K("C-w"),
        K("Super-Shift-t"): K("C-Shift-t"),
        K("Super-r"): K("C-r"),
        K("Super-Shift-left_brace"): K("C-page_up"),
        K("Super-Shift-right_brace"): K("C-page_down"),
        K("Super-p"): K("C-p"),
        K("Super-Shift-p"): K("C-Shift-p"),
        K("Super-comma"): K("C-comma"),
        K("Super-slash"): K("C-slash"),
        K("M-left"): K("C-left"),
        K("M-right"): K("C-right"),
    },
    "Default mac-style for non-terminal use."
)
