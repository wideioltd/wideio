#!/usr/bin/env python
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
from unittest import TestCase

from betamax import Betamax
from requests import Session
from wideio import llapi

with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes_v0'


class TestWIDEIOAPI(TestCase):
    def setUp(self):
        self.session = Session()

    def test_read_algorithm_schema(self):
        with Betamax(self.session) as vcr:
            vcr.use_cassette('user_reflect_algorithm')
            a = llapi.Api(session=self.session)
            a.collections.science.algorithm.schema()

    def test_read_algorithm_list(self):
        with Betamax(self.session) as vcr:
            vcr.use_cassette('user_list_algorithm')
            a = llapi.Api(session=self.session)
            a.collections.science.algorithm.list()

    def test_get_algorithm(self):
        with Betamax(self.session) as vcr:
            vcr.use_cassette('user_get_algorithm')
            a = llapi.Api(session=self.session)
            LA = a.collections.science.algorithm.list()
            a0 = a.collections.science.algorithm.get(a.collections, id=LA[0]["id"])
            assert hasattr(a0, "name")
            assert not hasattr(a0, "fldfal name")
            assert isinstance(a0.__dict__(), dict)

            # print "a0", a0
            # print "a0._dict__d", a0._dict__d, type(a0._dict__d)
            # print "a0.__dict__", a0.__dict__()
            # print dir(a0)
            # assert(False)
            # print "a0.image", a0.image
            # print "a0", a0
            #print a0.name
            #print dir(a0)
            #i0 = a0.image
            #print "i0", i0
            #print i0.name
            #print "adding request"
            #print a.collections.compute.execrequest.add(
            #    dict(algorithm=a0.id,
            #         parameters={'a': 2},
            #         inputs={'b': 3}
            #         )
            #)
