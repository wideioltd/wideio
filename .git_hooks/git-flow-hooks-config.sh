VERSION_FILE="VERSION"
_VERSION_FILE="$(for d in . .. ../..; do[ -f $d/setup.py ] | grep ^VERSION_FILE $d/setup.py; done)"
if [ "$_VERSION_FILE" ]; then
  VERSION_FILE=$_VERSION_FILE
fi


