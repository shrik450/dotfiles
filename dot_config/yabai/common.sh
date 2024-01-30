current_space() {
    yabai -m query --spaces --space
}

current_space_id() {
    current_space | jq -re ".index"
}

current_space_windows() {
    yabai -m query --windows --space $(current_space_id)
}

current_window() {
    yabai -m query --windows --window
}

current_window_id() {
    current_window | jq ".id"
}

current_window_in_stack() {
    local stack_index=current_window | jq ".\"stack-index\""
    if [ $stack_index = 0 ] then 1 else 0
}
