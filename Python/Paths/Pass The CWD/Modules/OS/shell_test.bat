@ECHO OFF
echo BEFORE "cd":
python direct_test.py
echo.
cd ..\
echo AFTER "cd":
python "Pass The CWD\direct_test.py"