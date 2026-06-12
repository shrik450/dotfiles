-- Dictation via Gemini (gemini_dictate.py). Hotkey or menubar click toggles:
-- start recording (red mic), press again to stop; the cleaned text is pasted
-- at the cursor. The API key lives in the keychain, not here.

local HOTKEY_MODS = { "alt", "shift" }
local HOTKEY_KEY = "g"
local UV = "/opt/homebrew/bin/uv"
local SCRIPT = os.getenv("HOME") .. "/.hammerspoon/gemini_dictate.py"

local MODELS = { "gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-3.1-pro-preview" }
local THINKING = { "off", "low", "high", "auto" }

local model = hs.settings.get("dictation.model") or MODELS[1]
local thinking = hs.settings.get("dictation.thinking") or THINKING[1]

local EXIT_MESSAGES = {
	[2] = "Dictation: no API key in keychain (service: gemini-dictation)",
	[3] = "Dictation: mic is silent — check Microphone permission",
	[4] = "Dictation: Gemini API error — check console",
	[5] = "Dictation: Gemini timed out — retry with --wav last.wav",
}

local task = nil
local stopping = false
local buffer = ""
local menubar = hs.menubar.new()
menubar:setTitle("🎙")

local soundStart = hs.sound.getByName("Pop")
local soundDone = hs.sound.getByName("Purr")

-- Paste via the clipboard: keyStrokes posts synthetic unicode events that
-- some apps drop (spaces especially). The previous contents are restored
-- only if the clipboard still holds our text by then.
local function insertText(text)
	local saved = hs.pasteboard.getContents()
	hs.pasteboard.setContents(text)
	local count = hs.pasteboard.changeCount()
	hs.eventtap.keyStroke({ "cmd" }, "v", 0)
	hs.timer.doAfter(0.4, function()
		if saved and hs.pasteboard.changeCount() == count then
			hs.pasteboard.setContents(saved)
		end
	end)
end

local function onExit(exitCode, stdOut, stdErr)
	task = nil
	stopping = false
	menubar:setTitle("🎙")
	local text = (buffer .. (stdOut or "")):gsub("^%s+", ""):gsub("%s+$", "")
	if exitCode == 0 then
		if text ~= "" then
			insertText(text)
			if soundDone then
				soundDone:play()
			end
		else
			hs.alert.show("Dictation: empty result")
		end
	else
		hs.alert.show(EXIT_MESSAGES[exitCode] or ("Dictation failed (exit " .. tostring(exitCode) .. ")"))
		if exitCode == 3 then
			hs.execute([[open "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"]])
		end
		print("dictation stderr: " .. (stdErr or ""))
	end
end

local function onStream(_, stdOut, stdErr)
	if stdOut and stdOut ~= "" then
		buffer = buffer .. stdOut
	end
	if stdErr and stdErr ~= "" then
		print("dictation: " .. stdErr)
	end
	return true
end

local function start()
	buffer = ""
	task = hs.task.new(UV, onExit, onStream, { "run", "--quiet", SCRIPT, "--model", model, "--thinking", thinking })
	task:setEnvironment({
		HOME = os.getenv("HOME"),
		PATH = "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
	})
	if not task:start() then
		task = nil
		hs.alert.show("Dictation: failed to start uv")
		return
	end
	menubar:setTitle("🔴")
	if soundStart then
		soundStart:play()
	end
end

local function stop()
	if task and not stopping then
		stopping = true
		menubar:setTitle("⏳")
		task:interrupt()
	end
end

local function toggle()
	if task then
		stop()
	else
		start()
	end
end

local function menu()
	local items = {
		{ title = task and "Stop & Transcribe" or "Start Dictation (⌥⇧G)", fn = toggle },
		{ title = "-" },
	}
	for _, m in ipairs(MODELS) do
		table.insert(items, {
			title = m,
			checked = m == model,
			fn = function()
				model = m
				hs.settings.set("dictation.model", m)
			end,
		})
	end
	table.insert(items, { title = "-" })
	for _, t in ipairs(THINKING) do
		table.insert(items, {
			title = "Thinking: " .. t,
			checked = t == thinking,
			fn = function()
				thinking = t
				hs.settings.set("dictation.thinking", t)
			end,
		})
	end
	return items
end

hs.hotkey.bind(HOTKEY_MODS, HOTKEY_KEY, toggle)
menubar:setMenu(menu)
