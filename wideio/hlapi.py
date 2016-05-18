# ############################################################################
# |W|I|D|E|I|O|L|T|D|W|I|D|E|I|O|L|T|D|W|I|D|E|I|O|L|T|D|W|I|D|E|I|O|L|T|D|
# Copyright (c) WIDE IO LTD
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# |D|O|N|O|T|R|E|M|O|V|E|!|D|O|N|O|T|R|E|M|O|V|E|!|D|O|N|O|T|R|E|M|O|V|E|!|
# ############################################################################
import logging
import llapi
import mimejson


class AlgoProxy(object):
    """
      import wideio.hlapi as hl;
      x=hl.Api()
      Usage: y = AlgoProxy(api, alg_id ) (at low level)
    """

    def __init__(self, api, a_id, webhook=None):
        self.api = api
        self.aid = a_id
        self.webhook = webhook

    def __call__(self, *args, **kwargs):
        with mimejson.MIMEJSON() as mj:
            aro = {}
            aro["algorithm"] = self.aid
            aro['parameters'] = mj.dumps(kwargs)
            aro['webhook'] = self.webhook
            self.api.collections.compute.algorithmrunorder.add(aro)
            logging.debug("Algo proxy was called")
            r = self.api.collections.compute.execrequest
            # todo finish this
        return r


class AlgoCollectionProxy(object):
    # calls a specified algorithm within specified constraint
    _L = None

    def __init__(self, api):
        self.api = api

    def __repr__(self):
        return "<* wio.api.hlapi.Api ** .algo instance " + hex(id(self)) + " *>"

    def __str__(self):
        return repr(self)

    def __getattr__(self, aname):
        if aname[0] == "_":
            raise ValueError
        r = self.api.collections.science.algorithm.list(name=aname)
        # todo:
        if len(r["res"]):
            return AlgoProxy(self.api, r["res"][0]["id"])  # first item in the "list"
        else:
            raise ValueError

    def __dir__(self, perpage=1000, maxres=50000):
        if self._L is None:
            page = 1
            cl = self.api.collections.science.algorithm.list(_PAGE=page, _PERPAGE=perpage)["res"]
            self._L = []
            while len(cl):
                for ci in cl:
                    self._L.append(ci["name"])
                    if len(self._L) > maxres:
                        logging.warning("Warning: Number of algorithm to be listed excessing __dir__ capacity \n")
                page += 1
                cl = self.api.collections.science.algorithm.list(_PAGE=page, _PERPAGE=perpage)["res"]  # can be empty
        return self._L


class Api(llapi.Api):
    """
    High Level API.

    Extends the API to allow to make synchronous calls to Algorithm in an easy way.

    This API is designed to make it easy to access specific class of algorithm and have
    an intuitive syntax for coding.
    """

    def __init__(self, *args, **kwargs):
        llapi.Api.__init__(self, *args, **kwargs)
        self.algo = AlgoCollectionProxy(self)
