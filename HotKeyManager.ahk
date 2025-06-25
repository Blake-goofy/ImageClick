#Requires AutoHotkey v2
#SingleInstance Force

iniFile := "config.ini"
hotkeyConfigs := []

; Find all sections starting with "Hotkey"
allSections := IniRead(iniFile)
for section in StrSplit(allSections, "`n") {
    if InStr(section, "Hotkey") = 1 {
        key    := IniRead(iniFile, section, "Key", "")
        folder := IniRead(iniFile, section, "Folder", "")
        window := IniRead(iniFile, section, "window", "")
        if key && folder && window {
            hotkeyConfigs.Push({key: key, folder: folder, window: window})
        }
    }
}

; Register hotkeys
for i, cfg in hotkeyConfigs {
    Hotkey(cfg.key, MakeHotkeyHandler(cfg))
}

MakeHotkeyHandler(cfg) {
    return (*) => HandleHotkey(cfg)
}

HandleHotkey(cfg, *) {
    activeTitle := WinGetTitle("A")
    if InStr(activeTitle, cfg.window) {
        unique := A_Now
        file := FileOpen("trigger.txt", "w")
        file.Write(cfg.folder "`n" unique)
        file.Close()
        return
    }
    ; Otherwise, pass hotkey through
    Hotkey(cfg.key, "Off")
    try {
        SendHotkeyString(cfg.key)
    } finally {
        Hotkey(cfg.key, (*) => HandleHotkey(cfg))
    }
}



SendHotkeyString(hk) {
    ; Function key handling, covers F1-F24 and modifiers
    if RegExMatch(hk, "^([~\^\!\+\#]*)(F\d{1,2})$", &m) {
        mods := m[1]
        key := m[2]
        Send(mods . "{" . key . "}")
    } else {
        Send(hk)
    }
}
