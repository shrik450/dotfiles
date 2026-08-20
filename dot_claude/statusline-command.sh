#!/bin/sh
input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // empty' | sed 's/Claude //; s/ (1M context)//')
tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // empty')
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')
five_used=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
week_used=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

out=""
[ -n "$model" ] && out="$model"
[ -n "$tokens" ] && out="$out | $(numfmt --to=si "$tokens")"
[ -n "$cost" ] && out="$out | $(printf '$%.2f' "$cost")"

limits=""
if [ -n "$five_used" ]; then
  five_left=$(printf '%.0f' "$(echo "100 - $five_used" | bc)")
  limits="5h:${five_left}%"
fi
if [ -n "$week_used" ]; then
  week_left=$(printf '%.0f' "$(echo "100 - $week_used" | bc)")
  limits="$limits 7d:${week_left}%"
fi
[ -n "$limits" ] && out="$out | $limits"

echo "$out"
