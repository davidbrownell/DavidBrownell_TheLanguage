import hashlib

class Sha256(object):
    def __init__(self):
        self._hasher = hashlib.sha256()

    def Update(self, data):
        self._hasher.update(data.encode("utf-8"))

    def Digest(self):
        return self._hasher.digest()
