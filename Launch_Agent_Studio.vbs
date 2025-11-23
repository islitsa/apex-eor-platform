' APEX EOR Platform - Agent Studio Launcher
' Double-click this file to start Agent Studio

Set WshShell = CreateObject("WScript.Shell")

' Get the directory where this script is located
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Change to the project directory
WshShell.CurrentDirectory = scriptDir

' Show a message that we're starting
MsgBox "Starting APEX Agent Studio..." & vbCrLf & vbCrLf & _
       "The application will open in your web browser in a few seconds." & vbCrLf & vbCrLf & _
       "Backend API: http://localhost:8000" & vbCrLf & _
       "Agent Studio: http://localhost:8501", vbInformation, "APEX EOR Platform"

' Start the batch file (hidden window)
WshShell.Run """" & scriptDir & "\launch_agent_studio_with_api.bat""", 0, False

' Wait 5 seconds for servers to start
WScript.Sleep 5000

' Open the browser
WshShell.Run "http://localhost:8501"
