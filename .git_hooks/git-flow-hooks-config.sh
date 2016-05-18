VERSION_FILE="VERSION"
_VERSION_FILE="$(for d in . .. ../.. ../../..; do [ -f $d/setup.py ] && grep ^VERSION_FILE $d/setup.py; done)"
if [ "$_VERSION_FILE" ]; then
  eval $(echo $_VERSION_FILE|td -d ' ')
fi
echo "VERSION_FILE=$VERSION_FILE" 1>&2
