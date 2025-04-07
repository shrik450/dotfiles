PaperWM = hs.loadSpoon("PaperWM")

PaperWM:bindHotkeys({
	-- switch to a new focused window in tiled grid
	focus_left = { { "alt", "ctrl" }, "h" },
	focus_right = { { "alt", "ctrl" }, "l" },
	focus_up = { { "alt", "ctrl" }, "k" },
	focus_down = { { "alt", "ctrl" }, "j" },

	-- move windows around in tiled grid
	swap_left = { { "alt", "ctrl", "shift" }, "h" },
	swap_right = { { "alt", "ctrl", "shift" }, "l" },
	swap_up = { { "alt", "ctrl", "shift" }, "k" },
	swap_down = { { "alt", "ctrl", "shift" }, "j" },

	-- position and resize focused window
	center_window = { { "alt", "ctrl" }, "c" },
	full_width = { { "alt", "ctrl" }, "f" },
	cycle_width = { { "alt", "ctrl" }, "r" },
	reverse_cycle_width = { { "ctrl", "alt", "cmd" }, "r" },
	cycle_height = { { "alt", "ctrl" }, "p" },
	reverse_cycle_height = { { "ctrl", "alt", "cmd", "shift" }, "r" },

	-- move focused window into / out of a column
	slurp_in = { { "alt", "ctrl" }, "i" },
	barf_out = { { "alt", "ctrl" }, "o" },

	-- move the focused window into / out of the tiling layer
	toggle_floating = { { "alt", "ctrl", "shift" }, "escape" },

	-- switch to a new Mission Control space
	switch_space_l = { { "alt", "ctrl" }, "," },
	switch_space_r = { { "alt", "ctrl" }, "." },
	switch_space_1 = { { "alt", "ctrl" }, "1" },
	switch_space_2 = { { "alt", "ctrl" }, "2" },
	switch_space_3 = { { "alt", "ctrl" }, "3" },
	switch_space_4 = { { "alt", "ctrl" }, "4" },
	switch_space_5 = { { "alt", "ctrl" }, "5" },
	switch_space_6 = { { "alt", "ctrl" }, "6" },
	switch_space_7 = { { "alt", "ctrl" }, "7" },
	switch_space_8 = { { "alt", "ctrl" }, "8" },
	switch_space_9 = { { "alt", "ctrl" }, "9" },

	-- move focused window to a new space and tile
	move_window_1 = { { "alt", "ctrl", "shift" }, "1" },
	move_window_2 = { { "alt", "ctrl", "shift" }, "2" },
	move_window_3 = { { "alt", "ctrl", "shift" }, "3" },
	move_window_4 = { { "alt", "ctrl", "shift" }, "4" },
	move_window_5 = { { "alt", "ctrl", "shift" }, "5" },
	move_window_6 = { { "alt", "ctrl", "shift" }, "6" },
	move_window_7 = { { "alt", "ctrl", "shift" }, "7" },
	move_window_8 = { { "alt", "ctrl", "shift" }, "8" },
	move_window_9 = { { "alt", "ctrl", "shift" }, "9" },
})
PaperWM.window_gap = 4
PaperWM.window_ratios = { 0.4, 0.5, 0.6 }
PaperWM:start()

-- Caffeinate menubar icon

Caffeine = hs.menubar.new()
function SetCaffeineDisplay(state)
	if state then
		Caffeine:setTitle("A")
	else
		Caffeine:setTitle("S")
	end
end

function CaffeineClicked()
	SetCaffeineDisplay(hs.caffeinate.toggle("displayIdle"))
end

if Caffeine then
	Caffeine:setClickCallback(CaffeineClicked)
	SetCaffeineDisplay(hs.caffeinate.get("displayIdle"))
end

-- Open Emacs in "quake mode"

local emacsVisible = false

function ToggleEmacsQuakeMode()
	if emacsVisible then
		HideEmacs()
	else
		ShowEmacs()
	end
end

function ShowEmacs()
	hs.application.launchOrFocus("Emacs")
	local emacsWindow = hs.window.find("Emacs")

	if emacsWindow then
		emacsWindow:focus()
		emacsVisible = true
	end
end

function HideEmacs()
	local emacsWindow = hs.window.find("Emacs")

	if emacsVisible then
		emacsWindow:minimize()
		emacsVisible = false
	end
end

hs.hotkey.bind({ "Cmd", "Shift" }, "I", ToggleEmacsQuakeMode, "Toggle Emacs Quake Mode")

-- Config auto reload

function ReloadConfig(files)
	local doReload = false
	for _, file in pairs(files) do
		if file:sub(-4) == ".lua" then
			doReload = true
		end
	end
	if doReload then
		hs.reload()
	end
end

MyWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", ReloadConfig):start()

hs.alert.show("Config loaded")
