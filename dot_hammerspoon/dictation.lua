-- Dictation via Gemini (gemini_dictate.py). Hotkey or menubar click toggles:
-- start recording (red mic), press again to stop; the cleaned text is pasted
-- at the cursor. A second hotkey re-sends the last recording when the API
-- fails. The API key lives in the keychain, not here.

local HOTKEY_MODS = { "alt", "shift" }
local HOTKEY_KEY = "g"
local RETRY_MODS = { "alt", "shift" }
local RETRY_KEY = "r"
local ADD_WORD_MODS = { "alt", "shift" }
local ADD_WORD_KEY = "d"
local UV = "/opt/homebrew/bin/uv"
local SCRIPT = os.getenv("HOME") .. "/.hammerspoon/gemini_dictate.py"
local WORDS_FILE = os.getenv("HOME") .. "/.hammerspoon/dictation_words.txt"
local LAST_WAV = os.getenv("HOME") .. "/.cache/gemini-dictation/last.wav"
local MAX_ENTRY_LENGTH = 200

local MODELS = { "gemini-3.7-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.5-flash" }
local THINKING = { "low", "high", "auto" }

local model = hs.settings.get("dictation.model") or MODELS[1]
local thinking = hs.settings.get("dictation.thinking") or THINKING[1]

local EXIT_MESSAGES = {
	[1] = "Dictation: cannot read the last recording — check console",
	[2] = "Dictation: no API key in keychain (service: gemini-dictation)",
	[3] = "Dictation: mic is silent — check Microphone permission",
	[4] = "Dictation: Gemini API error — press ⌥⇧R to retry",
	[5] = "Dictation: Gemini timed out — press ⌥⇧R to retry",
}

local task = nil
local mode = nil -- "record" or "retry" while a task runs
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
	mode = nil
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

-- Spawns the script with the current model and thinking settings. extraArgs
-- adds --wav for a retry; without it the script records from the mic.
local function launch(extraArgs)
	buffer = ""
	local args = { "run", "--quiet", SCRIPT, "--model", model, "--thinking", thinking }
	for _, a in ipairs(extraArgs or {}) do
		table.insert(args, a)
	end
	task = hs.task.new(UV, onExit, onStream, args)
	task:setEnvironment({
		HOME = os.getenv("HOME"),
		PATH = "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
	})
	if not task:start() then
		task = nil
		hs.alert.show("Dictation: failed to start uv")
		return false
	end
	return true
end

local function start()
	if not launch(nil) then
		return
	end
	mode = "record"
	menubar:setTitle("🔴")
	if soundStart then
		soundStart:play()
	end
end

-- Re-sends the newest recording to Gemini with the settings selected now,
-- not the ones used the first time.
local function retry()
	if task then
		hs.alert.show("Dictation: already running")
		return
	end
	if not hs.fs.attributes(LAST_WAV) then
		hs.alert.show("Dictation: no recording to retry")
		return
	end
	if not launch({ "--wav", LAST_WAV }) then
		return
	end
	mode = "retry"
	menubar:setTitle("⏳")
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

local function trim(s)
	return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

-- True if the file already holds this entry, ignoring surrounding whitespace
-- and case, so repeated adds do not pile up duplicates.
local function alreadyListed(entry)
	local f = io.open(WORDS_FILE, "r")
	if not f then
		return false
	end
	local wanted = entry:lower()
	for line in f:lines() do
		if trim(line):lower() == wanted then
			f:close()
			return true
		end
	end
	f:close()
	return false
end

-- Appends one dictionary entry: either a preferred spelling ("AllSpice") or a
-- correction rule ("no ERC -> NoERC"). The script re-reads the file on every
-- run, so the entry applies to the next dictation.
local function addEntry(entry)
	entry = trim(entry or "")
	if entry == "" then
		hs.alert.show("Dictation: nothing to add")
		return
	end
	if entry:find("\n") then
		hs.alert.show("Dictation: entry must be a single line")
		return
	end
	if #entry > MAX_ENTRY_LENGTH then
		hs.alert.show("Dictation: entry is too long")
		return
	end
	if alreadyListed(entry) then
		hs.alert.show("Dictation: already in dictionary — " .. entry)
		return
	end
	local f = io.open(WORDS_FILE, "a")
	if not f then
		hs.alert.show("Dictation: cannot write " .. WORDS_FILE)
		return
	end
	f:write(entry .. "\n")
	f:close()
	hs.alert.show("Dictation: added " .. entry)
end

local function addFromClipboard()
	addEntry(hs.pasteboard.getContents())
end

-- Prefills the box with the clipboard, so a correction rule takes one paste
-- plus the arrow and the right-hand side.
local function addTyped()
	local button, text = hs.dialog.textPrompt(
		"Add to dictionary",
		'A spelling, or a rule like "no ERC -> NoERC"',
		trim(hs.pasteboard.getContents() or ""),
		"Add",
		"Cancel"
	)
	if button == "Add" then
		addEntry(text)
	end
end

local function menu()
	local toggleTitle
	if mode == "record" then
		toggleTitle = "Stop & Transcribe"
	elseif mode == "retry" then
		toggleTitle = "Cancel Retry"
	else
		toggleTitle = "Start Dictation (⌥⇧G)"
	end
	local items = {
		{ title = toggleTitle, fn = toggle },
		{
			title = "Retry Last Recording (⌥⇧R)",
			disabled = task ~= nil or hs.fs.attributes(LAST_WAV) == nil,
			fn = retry,
		},
		{ title = "-" },
		{ title = "Add Clipboard to Dictionary (⌥⇧D)", fn = addFromClipboard },
		{ title = "Add to Dictionary…", fn = addTyped },
		{
			title = "Edit Dictionary…",
			fn = function()
				hs.execute("open -t '" .. WORDS_FILE .. "'")
			end,
		},
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
hs.hotkey.bind(RETRY_MODS, RETRY_KEY, retry)
hs.hotkey.bind(ADD_WORD_MODS, ADD_WORD_KEY, addFromClipboard)
menubar:setMenu(menu)
