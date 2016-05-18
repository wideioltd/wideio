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
"""
THE LOW LEVEL WIDE IO API

This class mirrors the API that is available on the server in a more
pythonic way.

Some elements are still missing such as actions, and virtual fields
are not yet mirrored yet.
"""
import json
import logging
import os
import sys
import requests
from mimejson import MIMEJSON

#    raise Exception, "FIXME: wjson seems buggy with long licence texts"
#    import wio.bridge.wjson as json


VERBOSITY = int(os.environ.get("WIO_API_VERBOSITY", os.environ.get("WIDEIO_API_VERBOSITY", "0")))
DEBUG = int(os.environ.get("WIO_API_DEBUG", os.environ.get("WIDEIO_API_DEBUG", "0")))
CONFIG_JSON_PATH = "~/.wideio-config.json"
CONFIG = {
    "site_url": os.environ.get("WIO_API_URL", "http://www.wide.io/"),
    "credentials": {"user": "admin", "password": "admin"}
}

pth = os.path.expanduser(CONFIG_JSON_PATH)

try:
    with open(pth, "r") as jsfile:
        jt = jsfile.read()
        jsfile.close()
        l = json.loads(jt)
        CONFIG.update(l)
except Exception as e:  # i.e. "No JSON object could be decoded"
    sys.stderr.write("[wio-api ]warning: could not load config file using default configuration (" + str(e) + ")\n")
# sys.stderr.write(str(e)+"\n")


_NAME = 0
_URL = 1
_SCHEMA = 2


def _dump(filename, string):
    text_file = open(filename, "w")
    text_file.write(string)
    text_file.close()


def lim_chars(st, maxlen=296):
    if len(st) > maxlen:
        st = str(st[0:maxlen]) + "..."
    return st


class RemoteException(Exception):
    pass


class ProxyException(Exception):
    def __init__(self, message):
        self.message = message


class ServerErrorException(ProxyException):
    def __init__(self, message, result):
        self.message = message
        self.result_info = result


class WIDEIOClient(object):
    def __init__(self, config, session=None):
        self.session = session or requests
        self.config = config
        self.result = None
        self.auth = (
            self.config["credentials"]["user"],
            self.config["credentials"]["password"]
        )
        self.args = {
            '_JSON': '1',
            '_AJAX': '1',
        }
        self.headers = {
            'Accept': 'application/json'
        }

        self.mjson = MIMEJSON(session=self.session)
        self.mjson.transport = self
        self.verbose = int(os.environ.get("WIO_API_VERBOSITY", self.config.get("verbose", 0)))
        self.verify = bool(int(os.environ.get("WIO_API_SSL_VERIFY", True)))

    def _parse_result(self, json):
        if "error" in json:
            raise RemoteException(json["error"])
        if "res" in json:
            return json["res"]
        return json

    def send(self, url, data=None, files=None):
        """
        send a POST request to the http server
        """
        self.result = None

        args = dict(self.args)
        if data is not None:
            args.update(data)

        t = (self.config["site_url"] + url, args, data, self.auth, files,)
        logging.debug(self, "POST( URL=%s arg=%r data_arg=%s auth=%r files=%r)" % t)
        # print "POST( URL=%s arg=%r data_arg=%s auth=%r files=%r)" % t

        self.result = self.session.post(self.config["site_url"] + url,
                                        data=args,
                                        auth=self.auth,
                                        files=files,
                                        verify=self.verify,
                                        headers=self.headers
                                        )
        t = self.result.text

        if not self.result.ok:
            if DEBUG:
                _dump("wideio_client.core", t)
            logging.debug(self, "   self.result: %r" % self.result)
            details = "" + str(self.result.reason) + " + " + str(self.result.status_code) + " + " + str(
                self.result.ok) + " +  " + self.result.raise_for_status()
            reason = "Error from server " + details
            raise ServerErrorException(reason, self.result)

        logging.debug(self, "\"result.text\" in json: %s\n" % (lim_chars(t),))
        logging.debug(self, "json.loads( " + lim_chars(t))

        obj = json.loads(t)
        return self._parse_result(obj)

    def request(self, url, query_mjson=None):
        """
        send with mimejson a request, mjson_dict should like:
            {
              data1  : 'data',
              file   : {'$mimetype$': 'file', '$path$': 'url or path'},
              image  : {'$mimetype$': 'image/jpg', '$path$': 'url or path'}
              infos++: []
            }
        """
        logging.debug(self, "send_mimejson_request")

        if query_mjson is None:
            return self.send(url)

        if isinstance(query_mjson, str):
            d = self.mjson.loads(query_mjson)
        else:
            d = self.mjson.loadd(query_mjson)

        a = self.mjson.push(d, url=url)

        logging.debug(self, ("%r" % (a,)))
        return a


def _clean_url(url):
    if url.startswith('/'):
        url = url[1:]
    if url.endswith('/'):
        url = url[:-1]
    return url


class APIClassMethodProxy(object):
    def __init__(self, parent, name):
        self.name = name
        self.parent = parent

    def __call__(self, __as_dict__=None, **arg):
        if __as_dict__ is not None:
            arg.update(__as_dict__)
        url = self.parent.url + self.name + '/'
        return self.parent._client.request(url, arg)


class APIMethodProxy(object):
    def __init__(self, parent, name, instance=None):
        self.name = name
        self.parent = parent
        self.instance = None

    def __call__(self, __as_dict__=None, **arg):
        if __as_dict__ is not None:
            arg.update(__as_dict__)
        oid = None
        if self.instance is None:
            if "id" not in arg.keys():
                raise Exception(("[wio-api] No instance specified"))

            oid = arg["id"]
            del arg["id"]
        else:
            oid = self.instance.id

        url = self.parent.url + self.name + '/' + oid + '/'
        return self.parent._client.request(url, arg)


class ProxyFK(object):
    """
    Foreign Key Wrapper.

    Used to resolve ForeignKey to other objects in the API
    """

    def __init__(self, db, table, key):
        self.db = db
        self.table = table
        self.key = key

    def __call__(self):
        obj = getattr(self.db, self.table[0])
        b = self.table[1]
        obj2 = getattr(obj, b)
        try:
            return obj2.get(self.db, id=self.key)
        except Exception as e:
            raise
            logging.warning("error while fetching ForeignKey :" + str(e))
            return None

            #
            # return getattr(getattr(self.api.collections, self.table[0]),
            #               self.table[1]).view(id=self.key)["res"]
            # doc: calls the view (on which object?),
            #  view(key)
            #  note: view is an instance of Instance method


def _make_std_property(y):
    def getter(_self):
        return getattr(_self, "_" + y[0])

    def setter(_self, v):
        setattr(_self, "_" + y[0], v)

    return property(getter, setter)


def _make_fk_property(xself, db, y):
    def getter(_self):
        apfk = ProxyFK(db, y[2][2][1], _self._dict__d[y[0] + "_id"])
        return apfk()

    return property(getter, None)


def APIModelProxy(xurl, infos):
    class _ProxyInstance(object):
        def __init__(self, db, t, d):
            self._db = db
            if isinstance(t, str):
                self.__type_desc = t.split(".")
                self.__col = getattr(getattr(db, self.__type_desc[0]), self.__type_desc[1])
            else:
                self.__type_desc = None
                self.__col = t

            self.__schema = self.__col.schema()
            self.__init_from_schema()
            if not isinstance(d, dict):
                try:
                    self._dict__d = self.__col.view(id=d)
                except Exception as e:
                    print "EXCEPTION", e
                    self._dict__d = None
            elif d is not None:
                self._dict__d = d
            self.init_from_dict(self._dict__d)

        def init_from_dict(self, d):
            for i in d.items():
                if "_" != i[0][0]:
                    setattr(self, "_" + i[0], i[1])
                    # print (self,"_"+i[0],i[1])

        def __dict__(self):
            r = {}
            for x in self.__schema:
                if hasattr(self, "_" + x[0]):
                    r[x[0]] = getattr(self, "_" + x[0])
            return r

        def __init_from_schema(self):
            for x in self.__schema:
                if x[2][0] != "ForeignKey":
                    p1 = _make_std_property(x)
                else:
                    p1 = _make_fk_property(self, self._db, x)
                setattr(self.__class__, x[0], p1)
                # print dir(getattr(self.__class__,x[0]))

        def save(self):
            self.__col.update(self._dict__dict__)

        def delete(self):
            self.__col.delete({'id': self.id})

    class _ProxyCollection(object):
        def __init__(self):
            # called by url = 'socialnetwork/comment'  or url = 'comment'
            # print("new ProxyCollection URL = %r" % url)
            url = xurl
            u = url.split('/')
            self.name = u[0]
            if '/' not in url:
                pass
                # make new collection of instance
                # raise Exception
                # url = url[url.index('/') + 1:]
                # if not hasattr(self, u[1]):
                #    setattr(self, u[1], ProxyCollection(url, infos))
            else:
                def _schema(self):
                    if self.__schema is None:
                        self.__schema = self.schema()
                    return self.__schema

                self._client = infos['client']
                self.model_name = infos['name']
                self.url = infos['full'] + '/'
                self.__schema = None

                for attr in infos['staticmethods']:
                    if not hasattr(self, attr):
                        setattr(self, attr, APIClassMethodProxy(self, attr))
                for attr in infos['instancemethods']:
                    if not hasattr(self, attr):
                        setattr(self, attr, APIMethodProxy(self, attr))

                self.__add_property('_schema', self.__schema, _schema)

        def dictobj_solve_fk(self, r):
            r = []
            for e in self._schema():
                if e[1] == "ForeignKey":
                    r[e[0]] = ProxyFK(self.api, e[3][1], r[e[0]])

        def __add_property(self, name, value, fget):
            def fset(_self, _value):
                _self._set_property(name, _value)

            setattr(self.__class__, name, property(fget, fset))
            setattr(self, '_' + name, value)

        def __set_property(self, name, value):
            setattr(self, '_' + name, value)

        def get(self, db, *args, **kwargs):
            return _ProxyInstance(db, self, self.view(*args, **kwargs))

    return _ProxyCollection()


class ProxyDatabase():
    def __init__(self, client):
        self.client = client
        self._models = []
        self.load_collections()

    def __getitem__(self, value):
        value = _clean_url(value)
        attr = self
        for val in value.split('/'):
            attr = getattr(attr, val)
        return attr

    def _get_col(self, m, staticmethods, instancemethods):
        url = _clean_url(m[_URL])
        if self.client.verbose >= 1:
            sys.stderr.write(m[_NAME] + "\t<-->\t" + url + "\n")
        infos = {
            'client': self.client, 'name': m[_NAME],
            'staticmethods': staticmethods,
            'instancemethods': instancemethods,
            'full': url
        }
        u = url.split('/')

        if not hasattr(self, u[0]):
            setattr(self, u[0], APIModelProxy(u[0], infos))  # which in turn calls the __init__
        if not hasattr(getattr(self, u[0]), u[1]):
            setattr(getattr(self, u[0]), u[1], APIModelProxy(url, infos))

        # attr=getattr(self, u[0])
        return url

    def load_collections(self):
        res = self.client.send('get_models/')
        self._all_models = res
        self._models = [self._get_col(m, ('add', 'list', 'schema'), ('update', 'delete', 'view'))
                        for m in self._all_models]
        self._aliases = {}
        for m in self._all_models:
            self._aliases[m[1].split("/")[2]] = m[1][1:]


class Api():
    def __init__(self, config=None, session=None):
        self.client = WIDEIOClient((config if config else CONFIG), session=session)
        self.collections = ProxyDatabase(self.client)
