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

' Check for Node.js
On Error Resume Next
result = WshShell.Run("node --version", 0, True)
If Err.Number <> 0 Or result <> 0 Then
    MsgBox "Node.js not found!" & vbCrLf & vbCrLf & _
           "Install Node.js from https://nodejs.org/", _
           vbCritical, "Telegram Exporter - Error"
    WScript.Quit 1
End If
On Error GoTo 0

' Change to script directory
WshShell.CurrentDirectory = ScriptDir

' Start FastAPI server silently in background
WshShell.Run pythonCmd & " web_server.py", 0, False

' Wait a moment for server to start
WScript.Sleep 3000

' Start React dev server silently in background
WshShell.CurrentDirectory = ScriptDir & "\web_ui"
WshShell.Run "cmd /c npm start", 0, False

' Wait a moment
WScript.Sleep 5000

' Open browser
WshShell.Run "http://localhost:3000", 1, False

' Show success message
MsgBox "Web interface started!" & vbCrLf & vbCrLf & _
       "Browser: http://localhost:3000" & vbCrLf & _
       "API: http://localhost:8000" & vbCrLf & vbCrLf & _
       "Note: The servers are running in the background." & vbCrLf & _
       "Use Task Manager to stop them if needed.", _
       vbInformation, "Telegram Exporter - Web UI"
