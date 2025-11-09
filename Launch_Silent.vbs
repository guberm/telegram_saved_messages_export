Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get script directory
ScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Try different Python commands
pythonCommands = Array("py", "python", "python3")
pythonFound = False

For Each cmd In pythonCommands
    On Error Resume Next
    result = WshShell.Run(cmd & " --version", 0, True)
    If Err.Number = 0 And result = 0 Then
        pythonCmd = cmd
        pythonFound = True
        Exit For
    End If
    On Error GoTo 0
Next

If Not pythonFound Then
    MsgBox "Python not found!" & vbCrLf & vbCrLf & _
           "Install Python from https://www.python.org/", _
           vbCritical, "Telegram Exporter - Error"
    WScript.Quit 1
End If

' Run the GUI without showing console
WshShell.CurrentDirectory = ScriptDir
WshShell.Run pythonCmd & " gui_visual.py", 0, False
