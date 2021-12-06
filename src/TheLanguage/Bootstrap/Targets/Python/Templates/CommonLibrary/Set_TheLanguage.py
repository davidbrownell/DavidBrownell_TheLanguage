class Set(object):
    def __init__(self, *values):
        self._values = set(values)

    def Empty(self):
        return bool(self._values)

    def NumElements(self):
        return len(self._values)

    def Capacity(self):
        return len(self._values)

    def Clear(self):
        self._values.clear()

    def Reserve_(self):
        pass

    def Resize_(self, new_size):
        pass

    @staticmethod
    def Create(*values):
        return Set(*values)

    def TryAdd(self, value):
        self._values.add(value)

    def Add_(self, value):
        return self.TryAdd(value)

    def TryAddUnique(self, value):
        self._values.add(value)

    def AddUnique_(self, value):
        return self.TryAddUnique(value)

    def TryRemove(self, value):
        self._values.discard(value)

    def Remove_(self, value):
        return self.TryRemove(value)

    def __getattr__(self, name):
        return getattr(self._values, name)

    def __eq__(self, other): return self.__class__.__Compare__(self, other) == 0
    def __ne__(self, other): return self.__class__.__Compare__(self, other) != 0
    def __lt__(self, other): return self.__class__.__Compare__(self, other) < 0
    def __le__(self, other): return self.__class__.__Compare__(self, other) <= 0
    def __gt__(self, other): return self.__class__.__Compare__(self, other) > 0
    def __ge__(self, other): return self.__class__.__Compare__(self, other) >= 0

    @classmethod
    def __Compare__(cls, a, b):
        if not isinstance(a, cls) or not isinstance(b, cls):
            return False

        if a._values < b._values: return -1
        if a._values > b._values: return 1

        return 0

    def __contains__(self, value):
        return value in self._values
