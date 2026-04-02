Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Gavrilo\Desktop\Files\WorkProjects\KacasBrickBreaker"
WshShell.Run "pythonw main.py", 0, False
