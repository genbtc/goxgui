@echo on
cd "C:\Users\EOFL\My Documents\GitHub\goxgui\goxgui\"
python C:\Python27\pyinstaller-2.0\pyinstaller.py goxgui.spec
move *.exe ..\
rmdir build /s /q 
del *.log