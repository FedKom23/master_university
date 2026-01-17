class CustomMeta(type):
    def __new__(mcs, name, bases, namespace):
        new_namespace = {}
        for k, v in namespace.items():
            if k.startswith('__') and k.endswith('__'):
                new_namespace[k] = v
            else:
                new_namespace[f'custom_{k}'] = v

        def custom_setattr(self, name, value):
            if name.startswith('__') and name.endswith('__'):
                object.__setattr__(self, name, value)
            else:
                object.__setattr__(self, f'custom_{name}', value)

        new_namespace["__setattr__"] = custom_setattr
        return super().__new__(mcs, name, bases, new_namespace)


class CustomClass(metaclass=CustomMeta):
    x = 50
    _z = 50

    def __init__(self, val=99):
        self.val = val

    def line(self):
        return 100

    def __str__(self):
        return "Custom_by_metaclass"
