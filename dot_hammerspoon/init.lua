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

hs.hotkey.bind({ "alt", "ctrl" }, "h", function()
	hs.window.filter.focusWest()
end)

hs.hotkey.bind({ "alt", "ctrl" }, "l", function()
	hs.window.filter.focusEast()
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
