"""
CLI Interface to WIDE IO.

This interface mimics the API and allows users to write scripts
for the WIDE IO platform.
"""
import json
import sys
from functools import partial

import llapi

COMMAND_ALIASES = {
    'ls': 'list',
    'ps': 'list',
    'create': 'add',
    'rm': 'delete',
    'get': 'view'
}


def main():
    a = llapi.Api()
    fqmdl = a.collections._aliases.get(sys.argv[1], sys.argv[1])
    app = fqmdl.split("/")[0]
    mdl = fqmdl.split("/")[1]

    colapp = getattr(a.collections, app)
    colmdl = getattr(colapp, mdl)
    methn = COMMAND_ALIASES.get(sys.argv[2], sys.argv[2])
    meth = getattr(colmdl, methn)
    if methn in ["get"]:
        meth = partial(meth, a.collections)

    sa = 3
    if methn not in ["list", "add", "get_schema"]:
        meth = partial(meth, id=sys.argv[sa])
        sa += 1

    kwargs = dict(zip(sys.argv[sa::2], sys.argv[(sa + 1)::2]))
    # TODO: need to validate and parse args
    res = meth(**kwargs)
    print json.dumps(res, indent=2)


if __name__ == "__main__":
    main()
