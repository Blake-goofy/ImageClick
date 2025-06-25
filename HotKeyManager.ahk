#SingleInstance Force

iniFile := "config.ini"
sectionHotkey := "Hotkey"
sectionWindows := "Windows"
keyName := "Key"
defaultHotkey := "F2"

hotkeyString := IniRead(iniFile, sectionHotkey, keyName, defaultHotkey)

windowTitles := []
index := 1
loop {
    key := "Title" index
    title := IniRead(iniFile, sectionWindows, key, "")
    if (title = "")
        break
    windowTitles.Push(title)
    index++
}

HotIf()
try {
    Hotkey(hotkeyString, (*) => RunImageClickIfWindow(hotkeyString))
} catch as e {
    MsgBox("Invalid hotkey in config.ini: " hotkeyString "`nError: " e.Message)
    ExitApp
}

RunImageClickIfWindow(hotkeyString) {
    global windowTitles
    activeTitle := WinGetTitle("A")
    for titleFilter in windowTitles {
        if InStr(activeTitle, titleFilter) {
            try {
                Run("ImageClick.exe")
                return
            } catch as e {
                MsgBox("Error: " e.Message)
                ExitApp
            }
        }
    }
    ; --- Not whitelisted, pass through hotkey ---
    Hotkey(hotkeyString, "Off")
    try {
        SendHotkeyString(hotkeyString)
    } finally {
        Hotkey(hotkeyString, (*) => RunImageClickIfWindow(hotkeyString))
    }
}

SendHotkeyString(hk) {
    ; For F1–F24, send as {F5}
    if RegExMatch(hk, "^([~\^\!\+\#]*)(F\d{1,2})$", &m) {
        mods := m[1]
        key := m[2]
        Send(mods . "{" . key . "}")
    } else {
        Send(hk)
    }
}