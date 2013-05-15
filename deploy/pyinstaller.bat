@echo on
cd "C:\Users\EOFL\My Documents\GitHub\goxgui\"
python C:\Python27\pyinstaller-2.0\pyinstaller.py goxgui.spec
move "C:\Users\EOFL\My Documents\GitHub\goxgui\dist\*.exe" "C:\Users\EOFL\My Documents\GitHub\goxgui\"
rmdir "C:\Users\EOFL\My Documents\GitHub\goxgui\dist\" /s /q 
rmdir "C:\Users\EOFL\My Documents\GitHub\goxgui\build\" /s /q 
