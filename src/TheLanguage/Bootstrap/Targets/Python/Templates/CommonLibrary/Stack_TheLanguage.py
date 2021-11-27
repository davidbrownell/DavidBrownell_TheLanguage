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

    def __eq__(self, other):
        return self._items == other._items
