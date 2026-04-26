from os import chdir
from os.path import dirname

#WHEN LAUNCHING A PYTHON FILE, IMPORTING ANOTHER PYTHON FILE,
#THAT DETECTS THE CWD OF THE IMPORTING PYTHON FILE, WITH "sys.argv[0]",
#MAKE SURE "os.chdir(os.path.dirname(__file__))", IS USED BEFORE IMPORTING,
#SO "sys.argv[0]" DOESN'T DETECT THE DEFAULT PYTHON PROFILE PATH.
chdir(dirname(__file__))
import direct_test
