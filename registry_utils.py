import winreg

class RegistryNode:
    __slots__ =  ["_name", "_key", "_values", "_value_iter", "closed"]
    datatypes = {
        bytes: winreg.REG_BINARY,
        int: winreg.REG_QWORD,
        str: winreg.REG_SZ
    }
    def __init__(self, key, name):
        #embed()
        self._name = name
        self._key = key
        self._values = {}
        self._value_iter = self._enum_values()
        self.closed = False

    @property
    def name(self):
        return self._name

    def _enum_values(self):
        # print("In enum.")
        try:
            for i in count(0):
                l, v, t = winreg.EnumValue(self._key, i)
                self._values[l] = (i, [v, t])
                yield l
        except OSError:
            pass

    def list_values(self):
        yield from self._values.keys()
        yield from self._enum_values()

    def get_value(self, k):
        if not k in self._values:
            try:
                for l in self._value_iter:
                    if l == k:
                        break
            except StopIteration:
                pass
        return self._values[k][1][0]

    def __getattr__(self, k):
        try:
            return super().__getattr__(k)
        except AttributeError:
            return self.get_value(k)

    def __setattr__(self, k, v):
        if k in self._slots:
            super().__setattr__(k, v)
        else:
            try:
                _ = getattr(self, k)
                self._values[k][1][0] = v
            except AttributeError:
                self._values[k] = (-1, [v, self.datatypes[type(v)]])
            winreg.SetValueEx(self._key, k, 0, self._values[k][1][1], v)


    def close(self):
        if not self.closed:
            self._key.Close()
            self.closed = True

    def __repr__(self):
        return "RegistryNode({})".format(
            ", ".join(repr(k) for k in (self._key, self._name))
        )

    def __dir__(self):
        return list(self._slots.union(set(self.list_values())))

RegistryNode._slots = set(RegistryNode.__slots__)