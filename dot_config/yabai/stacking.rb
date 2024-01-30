require_relative "common"

def window_in_stack?(window) = window["stack-index"] != 0

def first_window_of_current_stack = yabai_query "--windows --window stack.first"

def last_window_of_current_stack = yabai_query "--windows --window stack.last"
