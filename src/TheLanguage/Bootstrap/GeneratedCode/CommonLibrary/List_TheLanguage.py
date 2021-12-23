class List(object):
    def __init__(self, *items):
        self._items = list(items)

    def Empty(self):
        return not self._items

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
        if not self._items:
            return None

        return self._items[index]

    def Peek_(self, index):
        result = self.TryPeek(index)
        assert result is not None

        return result

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

    def Append_(self, value):
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

    def __setitem__(self, index, value):
        self._items[index] = value
        return self

    def __getitem__(self, index):
        return self._items[index]

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

    def __contains__(self, value):
        return value in self._items

    def __iadd__(self, other):
        assert isinstance(other, type(self)), (self, other)
        self._items += other._items
        return self
