class CustomList(list):
    def __init__(self, *args):
        super().__init__(*args)

    def _process_list_like(self, op, other, flg_sum):
        """Process list-like objects (CustomList or list)"""
        max_len = max(len(op), len(other))
        for i in range(max_len):
            if i >= len(op):
                value = other[i] if flg_sum else -other[i]
                op.append(value)
            elif i < len(other):
                if flg_sum:
                    op[i] += other[i]
                else:
                    op[i] -= other[i]
        return op

    def process_func(self, other, flg_sum):
        op = CustomList(self)
        if other.__class__ in (op.__class__, list):
            return self._process_list_like(op, other, flg_sum)
        if isinstance(other, int) and not isinstance(other, bool):
            for i, _ in enumerate(op):
                if flg_sum:
                    op[i] += other
                else:
                    op[i] -= other
            return op
        raise TypeError("неправильный тип")

    def __add__(self, other):
        return self.process_func(other, True)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.process_func(other, False)

    def __rsub__(self, other):
        op = CustomList(self)
        for i, _ in enumerate(op):
            op[i] *= -1
        return op.__add__(other)

    def __lt__(self, other):
        if other.__class__ == self.__class__:
            return sum(self) < sum(other)
        return NotImplemented

    def __gt__(self, other):
        if other.__class__ == self.__class__:
            return sum(self) > sum(other)
        return NotImplemented

    def __le__(self, other):
        if other.__class__ == self.__class__:
            return sum(self) <= sum(other)
        return NotImplemented

    def __ge__(self, other):
        if other.__class__ == self.__class__:
            return sum(self) >= sum(other)
        return NotImplemented

    def __eq__(self, other):
        if other.__class__ == self.__class__:
            return sum(self) == sum(other)
        return NotImplemented

    def __ne__(self, other):
        if other.__class__ == self.__class__:
            return sum(self) != sum(other)
        return NotImplemented

    def __str__(self):
        return f"элементы: {list(self)}, сумма: {sum(self)}"
