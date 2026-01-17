import unittest
from lru_cache import LRUCache


class TestLRUCache(unittest.TestCase):

    def setUp(self):
        self.cache = LRUCache(3)

    def test_init(self):
        """тест инициализации кеша"""
        self.assertEqual(self.cache.limit, 3)
        self.assertEqual(len(self.cache.cache), 0)
        self.assertIsNotNone(self.cache.head)
        self.assertIsNotNone(self.cache.tail)
        self.assertEqual(self.cache.head.next, self.cache.tail)
        self.assertEqual(self.cache.tail.prev, self.cache.head)

    def test_set_and_get(self):
        """тест добавления и получения элементов"""
        self.cache.set('a', 1)
        self.cache.set('b', 2)
        self.cache.set('c', 3)

        self.assertEqual(self.cache.get('a'), 1)
        self.assertEqual(self.cache.get('b'), 2)
        self.assertEqual(self.cache.get('c'), 3)

    def test_get_nonexistent_key(self):
        """тест получения несуществующего ключа"""
        self.assertIsNone(self.cache.get('nonexistent'))

    def test_overwrite_existing_key(self):
        """проверка перезаписи существующего ключа"""
        self.cache.set('a', 1)
        self.cache.set('a', 100)
        self.assertEqual(self.cache.get('a'), 100)
        self.assertEqual(len(self.cache.cache), 1)

    def test_lru_eviction(self):
        """тест вытеснения наименее используемого элемента"""
        self.cache.set('a', 1)
        self.cache.set('b', 2)
        self.cache.set('c', 3)
        self.cache.set('d', 4)
        self.assertIsNone(self.cache.get('a'))
        self.assertEqual(self.cache.get('b'), 2)
        self.assertEqual(self.cache.get('c'), 3)
        self.assertEqual(self.cache.get('d'), 4)
        self.assertEqual(len(self.cache.cache), 3)

    def test_lru_change_cache(self):
        """проверка изменения кэша после вытеснения самого редкого желемента"""
        self.cache.set('a', 1)
        self.cache.set('b', 2)
        self.cache.set('c', 3)
        self.cache.get('a')
        self.cache.set('d', 4)
        self.assertIsNone(self.cache.get('b'))
        self.assertEqual(self.cache.get('a'), 1)
        self.assertEqual(self.cache.get('c'), 3)
        self.assertEqual(self.cache.get('d'), 4)

    def test_lru_change_cache_after_change_value(self):
        """тест изменения кэша после перезаписи элемента"""
        self.cache.set('a', 1)
        self.cache.set('b', 2)
        self.cache.set('c', 3)
        self.cache.set('a', 100)
        self.cache.set('d', 4)
        self.assertIsNone(self.cache.get('b'))
        self.assertEqual(self.cache.get('a'), 100)
        self.assertEqual(self.cache.get('c'), 3)
        self.assertEqual(self.cache.get('d'), 4)

    def test_square_bracket(self):
        """проверка обращения квадратными скобками"""
        self.cache['a'] = 1
        self.cache['b'] = 2

        self.assertEqual(self.cache['a'], 1)
        self.assertEqual(self.cache['b'], 2)

    def test_limit_one(self):
        """тест кеша с размером 1"""
        cache = LRUCache(1)
        cache.set('a', 1)
        cache.set('b', 2)
        self.assertIsNone(cache.get('a'))
        self.assertEqual(cache.get('b'), 2)

    def test_limit_zero(self):
        """тест кеша с размером 0"""
        cache = LRUCache(0)
        cache.set('a', 1)
        self.assertIsNone(cache.get('a'))
        self.assertEqual(len(cache.cache), 0)


if __name__ == '__main__':
    unittest.main()
