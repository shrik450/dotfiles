local wezterm = require("wezterm")
local appearance = require("appearance")

local config = wezterm.config_builder()

if appearance.is_dark() then
	config.color_scheme = "GitHub Dark"
else
	config.color_scheme = "Github (base16)"
end

config.font = wezterm.font({ family = "SF Mono" })
config.font_size = 13.0

config.window_decorations = "RESIZE|INTEGRATED_BUTTONS"

config.window_frame = {
	font = wezterm.font({ family = "SF Mono" }),
	font_size = 11.0,
}

config.set_environment_variables = {
	PATH = "/opt/homebrew/bin:" .. os.getenv("PATH"),
}

config.keys = {
	{
		key = "LeftArrow",
		mods = "OPT",
		action = wezterm.action.SendString("\x1bb"),
	},
	{
		key = "RightArrow",
		mods = "OPT",
		action = wezterm.action.SendString("\x1bf"),
	},
	{
		key = ",",
		mods = "SUPER",
		action = wezterm.action.SpawnCommandInNewTab({
			cwd = wezterm.home_dir,
			args = { "nvim", wezterm.config_file },
		}),
	},
}

return config
