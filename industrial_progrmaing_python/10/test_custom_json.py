import unittest
import custom_json


class TestCustomJson(unittest.TestCase):
    """тесты для модуля custom_json"""

    def test_empty_object(self):
        """тест парсинга пустого словаря"""
        self.assertEqual(custom_json.loads("{}"), {})

    def test_single_int(self):
        """тест парсинга словаря с одним числом"""
        self.assertEqual(custom_json.loads('{"a":1}'), {"a": 1})

    def test_single_string(self):
        """тест парсинга словаря с одной строкой"""
        self.assertEqual(custom_json.loads('{"a":"x"}'), {"a": "x"})

    def test_multiple_pairs(self):
        """тест парсинга словаря с числами и строкаой"""
        s = '{"a":1,"b":"x","c":-5}'
        self.assertEqual(
            custom_json.loads(s),
            {"a": 1, "b": "x", "c": -5}
        )

    def test_whitespace(self):
        """тест парсинга с пробелами"""
        s = ' {  "a" :  1 ,  "b" : "x" } '
        self.assertEqual(
            custom_json.loads(s),
            {"a": 1, "b": "x"}
        )

    def test_missing_brace(self):
        """тест ошибки при отсутствии фигурной скобки"""
        with self.assertRaises(ValueError):
            custom_json.loads('"a":1')

    def test_unterminated_object(self):
        """тест ошибки при незакрытой строке"""
        with self.assertRaises(ValueError):
            custom_json.loads('{"a":1')

    def test_trailing_garbage(self):
        """тест ошибки при лишних символах"""
        with self.assertRaises(ValueError):
            custom_json.loads('{"a":1} xyz')

    def test_missing_colon(self):
        """тест ошибки при отсутствии двоеточия"""
        with self.assertRaises(ValueError):
            custom_json.loads('{"a" 1}')

    def test_missing_brace_left(self):
        """тест ошибки при отсутствии левой скобки"""
        with self.assertRaises(ValueError):
            custom_json.loads('"a" 1}')

    def test_empty_value(self):
        """тест ошибки при пустом значении"""
        with self.assertRaises(ValueError):
            custom_json.loads('{"a":}')

    def test_extra_comma(self):
        """тест ошибки при лишней запятой"""
        with self.assertRaises(ValueError):
            custom_json.loads('{"a":1,}')

    def test_non_string_key(self):
        """тест ошибки при нестроковом ключе."""
        with self.assertRaises(ValueError):
            custom_json.loads('{a:1}')

    def test_invalid_number(self):
        """тест ошибки при неверном формате числа"""
        with self.assertRaises(ValueError):
            custom_json.loads('{"a":12x}')

    def test_key_value_mismatch(self):
        """тест ошибки при несоответствии ключей и значений"""
        with self.assertRaises(ValueError):
            custom_json.loads('{"a":1,"b"}')

    def test_empty_dict(self):
        """тест  пустого словаря"""
        self.assertEqual(custom_json.dumps({}), "{}")

    def test_non_string_key_dumps(self):
        """тест ошибки при нестроковом ключе в dumps"""
        with self.assertRaises(ValueError):
            custom_json.dumps({1: "x"})

    def test_invalid_value_type_dumps(self):
        """тест ошибки при неподдерживаемом типе значения в dumps"""
        with self.assertRaises(ValueError):
            custom_json.dumps({"a": []})

    def test_round_trip(self):
        """тест обратимости операций loads/dumps"""
        data = {"a": 1, "b": "x", "c": -10}
        dumped = custom_json.dumps(data)
        loaded = custom_json.loads(dumped)
        self.assertEqual(loaded, data)


if __name__ == "__main__":
    unittest.main()
