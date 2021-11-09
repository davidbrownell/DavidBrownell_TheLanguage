class List(object):
    def __init__(self, *items):
        self._items = list(items)

    def Empty(self):
        return bool(self._items)

    def NumElements(self):
        return len(self._items)

    def Capacity(self):
        return len(self._items)

    def Clear(self):
        self._items.clear()

    def Reserve_(self, num_elements):
        pass

    def Resize_(self, num_elements):
        pass # BugBug

    def TryPeek(self, index):
        return self._items[index]

    def Peek_(self, index):
        return self.Peek_(index)

    @staticmethod
    def Create(*items):
        return List(*items)

    def Insert_(self, index, value):
        self._items.insert(index, value)

    def TryInsertFront(self, value):
        self._items.insert(0, value)

    def InsertFront_(self, value):
        return self.TryInsertFront(value)

    def TryInsertBack(self, value):
        self._items.append(value)

    def InsertBack_(self, value):
        return self.TryInsertBack(value)

    def TryRemove(self, index):
        del self._items[index]

    def Remove_(self, index):
        return self.TryRemove(index)

    def TryRemoveFront(self):
        return self.TryRemove(0)

    def RemoveFront_(self):
        return self.TryRemoveFront()

    def TryRemoveBack(self):
        return self.TryRemove(self.NumElements() - 1)

    def RemoveBack_(self):
        return self.TryRemoveBack()

    def __getattr__(self, name: str):
        return getattr(self._items, name)
