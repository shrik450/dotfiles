#!/bin/bash

# Terminate already running bar instances
killall -q polybar

# Wait until the processes have been shut down
while pgrep -u $UID -x polybar >/dev/null; do sleep 1; done

# Launch Polybar, using default config location ~/.config/polybar/config
# I only want this on my primary monitor
# but the name keeps changing.
# the only constant is HDMI
for m in $(polybar --list-monitors | cut -d":" -f1 | grep HDMI); do
    MONITOR=$m polybar --reload mybar &
done

echo "Polybar launched..."
