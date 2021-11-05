#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#MenuMaskKey vk07  ;Takes the extra CTRL event out of Alt+ hotkeys.
SetKeyDelay, -1, 50  ;Simulates holding down the key for 50ms.



ControlSend, , ^+{[}, ahk_exe obs64.exe
return