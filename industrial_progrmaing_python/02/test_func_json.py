import json
import unittest
from func_json import process_json


class TestProcessJson(unittest.TestCase):
    def test_basic_match(self):
        "проверяем базовый случай(1пример)"
        json_str = '{"key1": "word1 word2"}'
        required_keys = ["key1"]
        tokens = ["word1"]
        results = []

        def cb(k, t):
            results.append((k, t))
            return f"{k}:{t}"

        process_json(json_str, required_keys, tokens, cb)
        self.assertEqual(results, [("key1", "word1")])

    def test_no_required_keys(self):
        "проверяем работу без необходимых ключей"
        json_str = '{"key1": "word1 word2"}'
        tokens = ["word1"]
        results = []

        process_json(json_str, None, tokens,
                     lambda k, t: results.append((k, t)))
        self.assertEqual(results, [])

    def test_no_tokens(self):
        "проверяем работу без неободимых токенов"
        json_str = '{"key1": "word1 word2"}'
        required_keys = ["key1"]
        results = []

        process_json(json_str, required_keys, None,
                     lambda k, t: results.append((k, t)))
        self.assertEqual(results, [])

    def test_invalid_json(self):
        "проверяем работу с неправильной json строкой"
        with self.assertRaises(json.JSONDecodeError):
            process_json("{invalid json}", ["key1"], ["word1"],
                         lambda k, t: None)

    def test_case_sensitive_keys(self):
        "проверяем чуствительность к регистру у ключей"
        json_str = '{"key1": "word1"}'
        required_keys = ["Key1"]
        tokens = ["word1"]
        results = []

        process_json(json_str, required_keys, tokens,
                     lambda k, t: results.append((k, t)))
        self.assertEqual(results, [])

    def test_case_insensitive_tokens(self):
        "проверяем чуствительность к регистру у токенов"
        json_str = '{"key1": "Word1 WORD2"}'
        required_keys = ["key1"]
        tokens = ["word1", "word2"]
        results = []

        def cb(k, t):
            results.append((k, t))
            return f"{k}:{t}"

        process_json(json_str, required_keys, tokens, cb)
        self.assertEqual(set(results),
                         {("key1", "Word1"), ("key1", "WORD2")})

    def test_multiple_tokens_found(self):
        "проверяем случай с совпадением нескольких токенов в строке"
        json_str = '{"key1": "word1 word2 word3"}'
        required_keys = ["key1"]
        tokens = ["word1", "word3"]
        results = []

        process_json(json_str, required_keys, tokens,
                     lambda k, t: results.append((k, t)))
        self.assertEqual(set(results), {("key1", "word1"), ("key1", "word3")})

    def test_no_token_matches(self):
        "проверяем случай отсутсвия нужных токенов"
        json_str = '{"key1": "aaa bbb"}'
        required_keys = ["key1"]
        tokens = ["ccc"]
        results = []

        process_json(json_str, required_keys, tokens,
                     lambda k, t: results.append((k, t)))
        self.assertEqual(results, [])

    def test_multiple_keys(self):
        "проверяем случай нахождения токенов с несколькими ключами"
        json_str = ('{"key1": "word1 word2", "key2": "word2 word3", '
                    '"key3": "word1"}')
        required_keys = ["key1", "key3"]
        tokens = ["word1", "word3"]
        results = []

        process_json(json_str, required_keys, tokens,
                     lambda k, t: results.append((k, t)))
        self.assertEqual(set(results), {("key1", "word1"), ("key3", "word1")})


if __name__ == "__main__":
    unittest.main()
