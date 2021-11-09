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
