def Range(start, stop):
    yield from range(start, stop)

def IntGenerator(start, end):
    yield from range(start, end)

def Min(a, b):
    return a if a < b else b

def Max(a, b):
    return a if a > b else b

def Enumerate(value):
    yield from enumerate(value)

def Sum(*args):
    return sum(*args)
