@ECHO OFF
echo BEFORE "cd":
python direct_test.py
echo.
cd ..\
echo AFTER "cd":
python "OS\direct_test.py"