import unittest
from three_descriptors import Data


class TestPriceDescriptor(unittest.TestCase):
    def test_valid_price(self):
        """проверка корректного присвоения целого положительного числа"""
        data = Data(10, "John", "2024-05-12")
        data.price = 50
        self.assertEqual(data.price, 50)

    def test_invalid_price_type(self):
        """выбрасывает ValueError, если не int"""
        data = Data(10, "John", "2024-05-12")
        for invalid in ("100", 10.5, None, [], {}, True):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    data.price = invalid

    def test_invalid_price_less_than_zero(self):
        """выбрасывает ValueError, если значение ≤ 0"""
        data = Data(10, "John", "2024-05-12")
        for invalid in (0, -1, -100):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    data.price = invalid

    def test_get_from_class_none(self):
        """обращение к Data.price == None"""
        self.assertEqual(Data.price, None)

    def test_invalid_price_does_not_change_value(self):
        """попытка установки невалидного значения не меняет текущее значение"""
        data = Data(100, "John", "2024-05-12")
        original_price = data.price

        with self.assertRaises(ValueError):
            data.price = -50

        self.assertEqual(data.price, original_price)
        self.assertEqual(data.price, 100)


class TestNameDescriptor(unittest.TestCase):
    def test_valid_name(self):
        """проверка корректного имени"""
        data = Data(100, "John", "2024-01-01")
        valid_names = ["Alice", "Bob", "A"]
        for name in valid_names:
            with self.subTest(name=name):
                data.name = name
                self.assertEqual(data.name, name)

    def test_invalid_name_type(self):
        """некорректный тип должен вызывать исключение"""
        data = Data(100, "John", "2024-01-01")
        for invalid in (123, None, True, [], {}):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    data.name = invalid

    def test_invalid_name_format(self):
        """проверка некорректных строк"""
        data = Data(100, "John", "2024-01-01")
        invalid_names = [
            "",
            "alice",
            "ALICE",
            "AlIcE",
            "Al1ce",
            "A-lice"
        ]
        for invalid in invalid_names:
            with self.subTest(name=invalid):
                with self.assertRaises(ValueError):
                    data.name = invalid

    def test_get_from_class_none(self):
        """обращение к Data.name == None"""
        self.assertEqual(Data.name, None)

    def test_invalid_name_does_not_change_value(self):
        """попытка установки невалидного имени не меняет текущее значение"""
        data = Data(100, "John", "2024-01-01")
        original_name = data.name

        with self.assertRaises(ValueError):
            data.name = "john"

        self.assertEqual(data.name, original_name)
        self.assertEqual(data.name, "John")


class TestTimeDescriptor(unittest.TestCase):
    def test_valid_time(self):
        """проверка корректного формата даты"""
        data = Data(200, "John", "2024-10-10")
        valid_dates = ["2024-01-01", "1999-12-31", "2025-10-12"]
        for date in valid_dates:
            with self.subTest(date=date):
                data.time = date
                self.assertEqual(data.time, date)

    def test_invalid_time_format(self):
        """неправильный формат даты вызывает исключение"""
        data = Data(200, "John", "2024-10-10")
        invalid_dates = [
            "24-01-01",
            "2024/01/01",
            "2024-1-01",
            "2024-01-1",
            "abcd-ef-gh",
            "20240101",
            20240101,
            None,
        ]
        for invalid in invalid_dates:
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    data.time = invalid

    def test_get_from_class_none(self):
        """обращение к Data.time == None."""
        self.assertEqual(Data.time, None)

    def test_invalid_time_does_not_change_value(self):
        """попытка установки невалидной даты не меняет текущее значение"""
        data = Data(200, "John", "2024-10-10")
        original_time = data.time

        with self.assertRaises(ValueError):
            data.time = "2024-13-01"

        self.assertEqual(data.time, original_time)
        self.assertEqual(data.time, "2024-10-10")


class TestDataIntegration(unittest.TestCase):
    def test_full_initialization(self):
        """проверка создания экземпляра Data"""
        d = Data(100, "Alice", "2025-10-12")
        expected = (100, "Alice", "2025-10-12")
        self.assertEqual((d.price, d.name, d.time), expected)

    def test_full_initialization_invalid_values(self):
        """полная проверка на неккоректных данных"""
        with self.assertRaises(ValueError):
            Data(-5, "Alice", "2025-10-12")
        with self.assertRaises(ValueError):
            Data(50, "alice", "2025-10-12")
        with self.assertRaises(ValueError):
            Data(50, "Alice", "25-10-12")

    def test_instance_independence(self):
        """значения одного экземпляра не влияют на другой экземпляр"""
        data1 = Data(100, "Alice", "2024-01-01")
        data2 = Data(200, "Bob", "2024-02-02")

        self.assertEqual(data1.price, 100)
        self.assertEqual(data1.name, "Alice")
        self.assertEqual(data1.time, "2024-01-01")

        self.assertEqual(data2.price, 200)
        self.assertEqual(data2.name, "Bob")
        self.assertEqual(data2.time, "2024-02-02")

        data1.price = 150
        data1.name = "Carol"
        data1.time = "2024-03-03"

        self.assertEqual(data2.price, 200)
        self.assertEqual(data2.name, "Bob")
        self.assertEqual(data2.time, "2024-02-02")

        self.assertEqual(data1.price, 150)
        self.assertEqual(data1.name, "Carol")
        self.assertEqual(data1.time, "2024-03-03")

    def test_specific_field_error_messages(self):
        """проверка конкретных сообщений об ошибках для каждого поля"""
        with self.assertRaisesRegex(
            ValueError, r"Некорректная цена"
        ):
            Data(-5, "Alice", "2025-10-12")

        with self.assertRaisesRegex(
            ValueError, r"Некорректное имя"
        ):
            Data(100, "alice", "2025-10-12")

        with self.assertRaisesRegex(
            ValueError, r"Некорректная дата"
        ):
            Data(100, "Alice", "25-10-12")

    def test_mixed_valid_invalid_initialization_preserves_state(self):
        """попытка создания с некорректными данными не создает частично
        инициализированный объект"""
        with self.assertRaises(ValueError):
            Data(-100, "ValidName", "2024-01-01")

        with self.assertRaises(ValueError):
            Data(100, "invalid", "2024-01-01")

        with self.assertRaises(ValueError):
            Data(100, "ValidName", "invalid-date")

    def test_multiple_invalid_assignments_preserve_state(self):
        """множественные неудачные попытки изменения не портят состояние
        объекта"""
        data = Data(500, "David", "2024-05-15")
        original_state = (data.price, data.name, data.time)

        with self.assertRaises(ValueError):
            data.price = -100

        with self.assertRaises(ValueError):
            data.name = "123"

        with self.assertRaises(ValueError):
            data.time = "2024-02-30"

        self.assertEqual((data.price, data.name, data.time), original_state)
        self.assertEqual(data.price, 500)
        self.assertEqual(data.name, "David")
        self.assertEqual(data.time, "2024-05-15")

    def test_instance_initialization_with_descriptors(self):
        """проверка, что дескрипторы работают корректно при инициализации"""
        instance1 = Data(100, "Alice", "2024-01-01")
        instance2 = Data(200, "Bob", "2024-02-02")
        instance3 = Data(300, "Carol", "2024-03-03")

        instance1.price = 150
        instance2.name = "Bobby"
        instance3.time = "2024-04-04"

        self.assertEqual(instance1.price, 150)
        self.assertEqual(instance1.name, "Alice")
        self.assertEqual(instance1.time, "2024-01-01")

        self.assertEqual(instance2.price, 200)
        self.assertEqual(instance2.name, "Bobby")
        self.assertEqual(instance2.time, "2024-02-02")

        self.assertEqual(instance3.price, 300)
        self.assertEqual(instance3.name, "Carol")
        self.assertEqual(instance3.time, "2024-04-04")


if __name__ == "__main__":
    unittest.main()
