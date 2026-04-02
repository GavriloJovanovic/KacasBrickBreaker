Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Gavrilo\Desktop\Files\WorkProjects\KacasBrickBreaker"
WshShell.Run """C:\Users\Gavrilo\AppData\Local\Programs\Python\Python314\pythonw.exe"" main.py", 0, False
