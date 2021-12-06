class Stack(object):
    def __init__(self, *items):
        self._items = list(items)

    def Empty(self):
        return bool(self._items)

    def NumItems(self):
        return len(self._items)

    def Capacity(self):
        return len(self._items)

    def Clear(self):
        self._items.clear()

    def Reserve_(self, num_items):
        pass

    def Resize_(self, num_items):
        pass

    def Peek(self):
        return self._items[-1]

    @staticmethod
    def Create(*items):
        return Stack(*items)

    def TryPush(self, value):
        self._items.append(value)

    def Push_(self, value):
        return self.TryPush(value)

    def TryPop(self):
        self._items.pop()

    def Pop_(self):
        return self.TryPop()

    def __getattr__(self, name):
        return getattr(self._items, name)

    def __len__(self):
        return len(self._items)

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

        if a._items < b._items: return -1
        if a._items > b._items: return 1

        return 0
