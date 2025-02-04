-- Tiling Config

-- Gap between windows and screen edges
WindowGap = 5

hs.hotkey.bind({ "alt", "ctrl", "shift" }, "h", function()
	local win = hs.window.focusedWindow()
	local f = win:frame()
	local screen = win:screen()
	local max = screen:frame()

	f.x = max.x + WindowGap
	f.y = max.y + WindowGap
	f.w = max.w / 2 - (2 * WindowGap)
	f.h = max.h - (2 * WindowGap)
	win:setFrame(f)
end)

hs.hotkey.bind({ "alt", "ctrl", "shift" }, "l", function()
	local win = hs.window.focusedWindow()
	local f = win:frame()
	local screen = win:screen()
	local max = screen:frame()

	f.x = max.x + (max.w / 2) + WindowGap
	f.y = max.y + WindowGap
	f.w = max.w / 2 - (2 * WindowGap)
	f.h = max.h - (2 * WindowGap)
	win:setFrame(f)
end)

hs.hotkey.bind({ "alt", "ctrl", "shift" }, "f", function()
	local win = hs.window.focusedWindow()
	local f = win:frame()
	local screen = win:screen()
	local max = screen:frame()

	f.x = max.x + WindowGap
	f.y = max.y + WindowGap
	f.w = max.w - (2 * WindowGap)
	f.h = max.h - (2 * WindowGap)
	win:setFrame(f)
end)

hs.hotkey.bind({ "alt", "ctrl" }, "h", function()
	hs.window.filter.focusWest()
end)

hs.hotkey.bind({ "alt", "ctrl" }, "l", function()
	hs.window.filter.focusEast()
end)

hs.hotkey.bind({ "alt", "ctrl" }, "n", function()
	local focused = hs.window.focusedWindow()
	if not focused then
		return {}
	end

	local focusedFrame = focused:frame()
	local allWindows = hs.window.orderedWindows()
	local samePositionWindows = {}

	for _, window in ipairs(allWindows) do
		local frame = window:frame()
		if math.abs(frame.x - focusedFrame.x) < 10 and math.abs(frame.y - focusedFrame.y) < 10 then
			table.insert(samePositionWindows, window)
		end
	end

	if #samePositionWindows <= 1 then
		return
	end

	local currentIndex = 1

	for i, window in ipairs(samePositionWindows) do
		if window:id() == focused:id() then
			currentIndex = i
			break
		end
	end

	local nextIndex = (currentIndex == 1) and #samePositionWindows or (currentIndex - 1)
	samePositionWindows[nextIndex]:focus()
end)

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

local emacsWindow = nil
local emacsVisible = false
local originalFrame = nil

function ToggleEmacsQuakeMode()
	if emacsVisible then
		HideEmacs()
	else
		ShowEmacs()
	end
end

function ShowEmacs()
	if emacsWindow == nil then
		hs.application.launchOrFocus("Emacs")
		emacsWindow = hs.window.find("Emacs")
	end

	if emacsWindow then
		local screen = hs.screen.mainScreen()
		local max = screen:frame()
		local quakeFrame = {
			x = max.x + (max.w / 2) + WindowGap,
			y = max.y + WindowGap,
			w = max.w / 2 - (2 * WindowGap),
			h = max.h - (2 * WindowGap),
		}
		emacsWindow:setFrame(quakeFrame)
		emacsWindow:focus()
		emacsVisible = true
	end
end

function HideEmacs()
	if emacsWindow then
		if originalFrame then
			emacsWindow:setFrame(originalFrame)
		else
			emacsWindow:minimize()
		end
		emacsWindow = nil
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
