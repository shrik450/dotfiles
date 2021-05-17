# -*- coding: utf-8 -*-
# autostart = true

from xkeysnail.transform import *

terminals = [
    "gnome-terminal",
    "konsole",
    "kitty",
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
        Key.LEFT_CTRL: Key.LEFT_META,
        Key.LEFT_META: Key.LEFT_CTRL
    }
)

define_keymap(
    None,
    {
        K("C-Shift-left_brace"): K("C-page_up"),
        K("C-Shift-right_brace"): K("C-page_down"),
    }
)

# define_keymap(
#     lambda wm_class: wm_class not in terminals,
#     {
#         K("Super-c"): K("C-c"),
#         K("Super-x"): K("C-x"),
#         K("Super-v"): K("C-v"),
#         K("Super-k"): K("C-k"),
#         K("Super-z"): K("C-z"),
#         K("Super-Shift-z"): K("C-Shift-z"),
#         K("Super-s"): K("C-s"),
#         K("Super-o"): K("C-o"),
#         K("Super-n"): K("C-n"),
#         K("Super-b"): K("C-b"),
#         K("Super-t"): K("C-t"),
#         K("Super-w"): K("C-w"),
#         K("Super-Shift-t"): K("C-Shift-t"),
#         K("Super-r"): K("C-r"),
#         K("Super-Shift-left_brace"): K("C-page_up"),
#         K("Super-Shift-right_brace"): K("C-page_down"),
#         K("Super-p"): K("C-p"),
#         K("Super-l"): K("C-l"),
#         K("Super-Shift-p"): K("C-Shift-p"),
#         K("Super-comma"): K("C-comma"),
#         K("Super-slash"): K("C-slash"),
#         K("Super-d"): K("C-d"),
#    },
#     "Default mac-style for non-terminal use."
# )
