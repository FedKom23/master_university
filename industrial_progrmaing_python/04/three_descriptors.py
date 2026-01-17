from abc import ABC, abstractmethod


class Base(ABC):

    def __init__(self):
        self._name = None

    def __set_name__(self, owner, name):
        self._name = f'_{name}'

    def __get__(self, instance, owner):
        if instance is None:
            return None
        return getattr(instance, self._name, None)

    def __set__(self, instance, value):
        if self.checker(value):
            setattr(instance, self._name, value)
        else:
            raise ValueError(self._get_error_message(value))

    @abstractmethod
    def checker(self, value):
        pass

    @abstractmethod
    def _get_error_message(self, value):
        pass


class Price(Base):
    def checker(self, value):
        return (isinstance(value, int) and not isinstance(value, bool)
                and value > 0)

    def _get_error_message(self, value):
        return f"Некорректная цена: '{value}'"


class Name(Base):
    def checker(self, value):
        if not (isinstance(value, str) and value):
            return False
        if not value[0].isupper():
            return False
        if not value.isalpha():
            return False
        if len(value) > 1 and not all(char.islower() for char in value[1:]):
            return False
        return True

    def _get_error_message(self, value):
        return f"Некорректное имя: '{value}'"


class Time(Base):
    def checker(self, value):
        if not isinstance(value, str):
            return False
        parts = value.split('-')
        if len(parts) != 3:
            return False
        year, month, day = parts
        if len(year) != 4 or len(month) != 2 or len(day) != 2:
            return False
        if not (year.isdigit() and month.isdigit() and day.isdigit()):
            return False
        year_int = int(year)
        month_int = int(month)
        day_int = int(day)
        if month_int < 1 or month_int > 12:
            return False
        if day_int < 1 or day_int > 31:
            return False
        if month_int == 2:
            is_leap = (
                (year_int % 4 == 0 and year_int % 100 != 0) or
                (year_int % 400 == 0)
            )
            max_day = 29 if is_leap else 28
            if day_int > max_day:
                return False
        elif month_int in [4, 6, 9, 11]:
            if day_int > 30:
                return False
        return True

    def _get_error_message(self, value):
        return f"Некорректная дата: '{value}'"


class Data:
    price = Price()
    name = Name()
    time = Time()

    def __init__(self, price, name, time):
        self.price = price
        self.name = name
        self.time = time
