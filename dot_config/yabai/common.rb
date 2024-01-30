require "json"

def yabai(args) = `yabai -m #{args}`

def yabai_query(args) = JSON.parse(yabai "query #{args}")

def current_space = yabai_query "--spaces --space"

def current_window = yabai_query "--windows --window"

def current_space_windows = yabai_query "--windows --space"

def non_minimized_windows(windows) = windows.reject { _1["is-minimized"] }
