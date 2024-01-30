require_relative "common"

def window_in_stack?(window) = window["stack-index"] != 0

def has_window_below?(window) = window["split-type"] == "horizontal" && window["split-child"] == "first_child"

def has_window_above?(window) = window["split-type"] == "horizontal" && window["split-child"] == "second_child"

def has_window_right?(window) = window["split-type"] == "vertical" && window["split-child"] == "first_child"

def has_window_left?(window) = window["split-type"] == "vertical" && window["split-child"] == "second_child"

def first_window_of_current_stack = yabai_query "--windows --window stack.first"

def last_window_of_current_stack = yabai_query "--windows --window stack.last"
