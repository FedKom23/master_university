import unittest
from unittest.mock import patch
from param_dec import retry_deco


class TestRetryDeco(unittest.TestCase):
    def test_add_positional_args(self):
        "проверка логгирования только позиционных аргументов"
        @retry_deco(3)
        def add(a, b):
            return a + b

        with patch("builtins.print") as mock_print:
            result = add(4, 2)

        self.assertEqual(result, 6)
        printed = " ".join(call[0][0] for call in mock_print.call_args_list)
        self.assertIn("args = (4, 2)", printed)
        self.assertIn("kwargs = {}", printed)
        self.assertIn("result = 6", printed)

    def test_add_keyword_args(self):
        "проверка логгирования позиционных и именованных аргументов"
        @retry_deco(3)
        def add(a, b):
            return a + b

        with patch("builtins.print") as mock_print:
            result = add(4, b=3)

        self.assertEqual(result, 7)
        printed = " ".join(call[0][0] for call in mock_print.call_args_list)
        self.assertIn("args = (4,)", printed)
        self.assertIn("kwargs = {'b': 3}", printed)
        self.assertIn("result = 7", printed)

    def test_check_str_success(self):
        "проверка логгирования только именованных аргументов"
        @retry_deco(3)
        def check_str(value=None):
            if value is None:
                raise ValueError()
            return isinstance(value, str)

        with patch("builtins.print") as mock_print:
            result = check_str(value="123")

        self.assertTrue(result)
        printed = " ".join(call[0][0] for call in mock_print.call_args_list)
        self.assertIn("result = True", printed)

    def test_check_raises_after_retries(self):
        "логгирование всех полного прохода попыток перезапуска"
        calls = []

        @retry_deco(3)
        def check_str(value=None):
            calls.append(value)
            if value is None:
                raise ValueError()
            return isinstance(value, str)

        with patch("builtins.print") as mock_print:
            result = check_str(value=None)

        self.assertIsNone(result)
        self.assertEqual(len(calls), 3)
        printed = " ".join(call[0][0] for call in mock_print.call_args_list)
        self.assertEqual(printed.count("exception = ValueError"), 3)

    def test_check_expected_exception(self):
        "проверка на совпадения исключения"
        calls = []

        @retry_deco(2, [ValueError])
        def check_int(value=None):
            calls.append(value)
            if value is None:
                raise ValueError()
            return isinstance(value, str)

        with patch("builtins.print") as mock_print:
            result = check_int(value=None)

        self.assertIsNone(result)
        self.assertEqual(len(calls), 1)
        printed = " ".join(call[0][0] for call in mock_print.call_args_list)
        self.assertEqual(printed.count("exception = ValueError"), 1)

    def test_decorator_without_arguments_success(self):
        "тест декоратора без аргументов"
        @retry_deco()
        def f(x):
            return x * 2

        with patch("builtins.print") as mock_print:
            result = f(5)

        self.assertEqual(result, 10)
        printed = " ".join(call[0][0] for call in mock_print.call_args_list)
        self.assertIn("result = 10", printed)

    def test_decorator_without_arguments_retry_once(self):
        "тест декоратора без аргументов с выбросом исключения"
        calls = []

        @retry_deco()
        def f(x):
            calls.append(x)
            raise RuntimeError("fail always")

        with patch("builtins.print") as mock_print:
            result = f(42)

        self.assertIsNone(result)
        self.assertEqual(len(calls), 1)
        printed = " ".join(call[0][0] for call in mock_print.call_args_list)
        self.assertEqual(printed.count("exception = RuntimeError"), 1)


if __name__ == "__main__":
    unittest.main()
