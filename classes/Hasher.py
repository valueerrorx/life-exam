#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# import hashlib


class Hasher():

    def getUniqueConnectionID(self, name, cid):  # noqa
        """ creates a md5 hash as connectionID """
        # str2hash = "%s-%s" % (name, cid)
        # result = hashlib.md5(str2hash.encode())
        # return result.hexdigest()
        return name
