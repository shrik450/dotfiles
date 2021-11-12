#! /bin/bash

# Load the other display using xrandr
xrandr --output DP-0 --primary --right-of HDMI-0

# Load wallpaper with feh
feh --bg-fill ~/wallpapers/4spdee0qw1971.jpg

# Load other services
ibus-daemon -dr


