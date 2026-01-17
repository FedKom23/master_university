import unittest
from customlist import CustomList


class TestCustomList(unittest.TestCase):

    def test_class(self):
        """ проверка на правильный тип экземпляра класса"""
        a = CustomList([1, 2, 3])
        self.assertIsInstance(a, CustomList)

    def test_str(self):
        """ проверка метода __str__ экземпляра клсса"""
        a = CustomList([1, 2, 3])
        b = CustomList([])
        self.assertEqual(str(a), "элементы: [1, 2, 3], сумма: 6")
        self.assertEqual(str(b), "элементы: [], сумма: 0")

    def test_add_with_customlist(self):
        """
            проверка сложения с обеих сторон
            у двух экземпляров кастомного класса
        """
        a = CustomList([5, 1, 3, 7])
        b = CustomList([1, 2, 7])
        result = a + b
        result2 = b + a
        self.assertIsInstance(result, CustomList)
        self.assertEqual(result, CustomList([6, 3, 10, 7]))

        self.assertIsInstance(result2, CustomList)
        self.assertEqual(result2, CustomList([6, 3, 10, 7]))

    def test_add_with_list(self):
        """проверка сложения с обеих сторон списка с экземпляром класса"""
        a = CustomList([2, 5])
        b = [10]
        result = a + b
        result2 = b + a
        self.assertIsInstance(result, CustomList)
        self.assertEqual(result, CustomList([12, 5]))

        self.assertIsInstance(result2, CustomList)
        self.assertEqual(result2, CustomList([12, 5]))

    def test_add_with_int(self):
        """проверка сложения с обеих сторон int числа"""
        a = CustomList([2, 5])
        result = a + 10
        result2 = 10 + a
        self.assertIsInstance(result, CustomList)
        self.assertEqual(result, CustomList([12, 15]))

        self.assertIsInstance(result2, CustomList)
        self.assertEqual(result2, CustomList([12, 15]))

    def test_sub_with_customlist(self):
        """
            проверка вычитания с обеих сторон
            у двух экземпляров кастомного класса
        """
        a = CustomList([5, 1, 3, 7])
        b = CustomList([1, 2, 7])
        result = a - b
        result2 = b - a

        self.assertIsInstance(result, CustomList)
        self.assertEqual(result, CustomList([4, -1, -4, 7]))

        self.assertIsInstance(result2, CustomList)
        self.assertEqual(result2, CustomList([-4, 1, 4, -7]))

    def test_sub_with_list(self):
        """проверка вычитания с обеих сторон списка с экземпляром класса"""
        a = CustomList([2, 5])
        b = [10]
        result = a - b
        result2 = b - a
        self.assertIsInstance(result, CustomList)
        self.assertEqual(result, CustomList([-8, 5]))

        self.assertIsInstance(result2, CustomList)
        self.assertEqual(result2, CustomList([8, -5]))

    def test_sub_with_int(self):
        """проверка вычитания с обеих сторон int числа"""
        a = CustomList([2, 5])
        result = a - 10
        result2 = 10 - a
        self.assertIsInstance(result, CustomList)
        self.assertEqual(result, CustomList([-8, -5]))

        self.assertIsInstance(result2, CustomList)
        self.assertEqual(result2, CustomList([8, 5]))

    def test_eq_compare_by_sum(self):
        """проверка опреанда =="""
        a = CustomList([1, 2, 3])
        b = CustomList([6])
        c = "a"
        self.assertTrue(a == b)
        self.assertFalse(a == c)

    def test_ne_compare_by_sum(self):
        """проверка опреанда !="""
        a = CustomList([1, 5, 3])
        b = CustomList([6])
        c = "a"
        self.assertTrue(a != b)
        self.assertTrue(a != c)

    def test_gt_lt_compare_by_sum(self):
        """проверка опреандов < и >"""
        a = CustomList([10])
        b = CustomList([2, 3])
        c = "a"
        self.assertTrue(a > b)
        self.assertFalse(a < b)
        with self.assertRaises(TypeError):
            _ = a < c
        with self.assertRaises(TypeError):
            _ = a > c

    def test_ge_le_compare_by_sum(self):
        """проверка опреандов <= и >="""
        a = CustomList([5, 5])
        b = CustomList([10])
        c = "a"
        self.assertTrue(a >= b)
        self.assertTrue(b <= a)
        with self.assertRaises(TypeError):
            _ = a <= c
        with self.assertRaises(TypeError):
            _ = a >= c

    def test_sub_with_empty_list(self):
        """проверка операции с пустым массивом и экземпляром класса"""
        a = CustomList([1, 2, 3])
        b = CustomList([])
        c = []
        result = a - b
        result2 = a - c
        self.assertEqual(result, CustomList([1, 2, 3]))
        self.assertEqual(result2, CustomList([1, 2, 3]))

    def test_add_invalid_type(self):
        """проверка операции с неправильным типом(str)"""
        a = CustomList([1, 2])
        with self.assertRaises(TypeError):
            _ = a + "abc"

    def test_sub_invalid_type(self):
        """проверка операции с None"""
        a = CustomList([1, 2])
        with self.assertRaises(TypeError):
            _ = a + None

    def test_add_with_bool_treated_as_int(self):
        """проверка операции с неправильным типом(bool)"""
        a = CustomList([1, 2])
        with self.assertRaises(TypeError):
            _ = a + True

    def test_immutability_after_operations(self):
        """проверка, что исходные списки остаются неизменными после операций"""
        a = CustomList([1, 2, 3])
        b = CustomList([4, 5])
        _ = a + b
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [4, 5])

        _ = a - b
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [4, 5])

        c = [6, 7, 8]
        _ = a + c
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(c, [6, 7, 8])

        _ = c + a
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(c, [6, 7, 8])

    def test_elementwise_comparison_for_addition(self):
        """поэлементная проверка сложения (не используя __eq__)"""
        a = CustomList([1, 2, 3, 4])
        b = [5, 6]
        result = a + b
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], 6)
        self.assertEqual(result[1], 8)
        self.assertEqual(result[2], 3)
        self.assertEqual(result[3], 4)

        a = CustomList([1, 2])
        b = [3, 4, 5, 6]
        result = a + b
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], 4)
        self.assertEqual(result[1], 6)
        self.assertEqual(result[2], 5)
        self.assertEqual(result[3], 6)

        a = CustomList([1, 2, 3])
        result = a + 5
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 6)
        self.assertEqual(result[1], 7)
        self.assertEqual(result[2], 8)

    def test_elementwise_comparison_for_subtraction(self):
        """поэлементная проверка вычитания (не используя __eq__)"""
        a = CustomList([10, 20, 30, 40])
        b = [5, 3]
        result = a - b
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], 5)
        self.assertEqual(result[1], 17)
        self.assertEqual(result[2], 30)
        self.assertEqual(result[3], 40)

        a = CustomList([10, 20])
        b = [5, 3, 1, 2]
        result = a - b
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], 5)
        self.assertEqual(result[1], 17)
        self.assertEqual(result[2], -1)
        self.assertEqual(result[3], -2)

        a = CustomList([10, 20, 30])
        result = a - 5
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 5)
        self.assertEqual(result[1], 15)
        self.assertEqual(result[2], 25)

    def test_different_size_operations_all_combinations(self):
        """проверка всех комбинаций размеров для сложения/вычитания"""
        test_cases = [
            (CustomList([1, 2]), [3, 4, 5], [4, 6, 5], [-2, -2, -5]),

            (CustomList([1, 2, 3]), [4, 5], [5, 7, 3], [-3, -3, 3]),

            (CustomList([1, 2, 3]), [4, 5, 6], [5, 7, 9], [-3, -3, -3]),

            (CustomList([]), [1, 2, 3], [1, 2, 3], [-1, -2, -3]),

            (CustomList([1, 2, 3]), [], [1, 2, 3], [1, 2, 3]),

            (CustomList([]), [], [], []),

            (CustomList([10]), [1, 2, 3], [11, 2, 3], [9, -2, -3]),

            (CustomList([1, 2, 3]), [10], [11, 2, 3], [-9, 2, 3]),
        ]

        for custom_list, other_list, expected_add, expected_sub in test_cases:
            with self.subTest(
                f"CL={list(custom_list)[:1]}, other={other_list[:1]}"
            ):
                result_add = custom_list + other_list
                self.assertEqual(list(result_add), expected_add)

                result_radd = other_list + custom_list
                self.assertEqual(list(result_radd), expected_add)

                result_sub = custom_list - other_list
                self.assertEqual(list(result_sub), expected_sub)

                result_rsub = other_list - custom_list
                expected_rsub = [-x for x in expected_sub]
                self.assertEqual(list(result_rsub), expected_rsub)

    def test_different_size_operations_with_other_customlist(self):
        """проверка операций с другим CustomList разного размера"""
        test_cases = [
            (
                CustomList([1, 2]), CustomList([3, 4, 5]),
                [4, 6, 5], [-2, -2, -5]
            ),
            (CustomList([1, 2, 3]), CustomList([4, 5]), [5, 7, 3], [-3, -3, 3]),
            (CustomList([]), CustomList([1, 2]), [1, 2], [-1, -2]),
            (CustomList([10]), CustomList([1, 2]), [11, 2], [9, -2]),
        ]

        for a, b, expected_add, expected_sub in test_cases:
            with self.subTest(f"a={a}, b={b}"):
                result_add = a + b
                self.assertEqual(list(result_add), expected_add)

                result_sub = a - b
                self.assertEqual(list(result_sub), expected_sub)

                self.assertNotEqual(id(result_add), id(a))
                self.assertNotEqual(id(result_add), id(b))

    def test_elementwise_comparison_using_str(self):
        """альтернатива: проверка через __str__, если не доверяем __eq__"""
        a = CustomList([1, 2, 3])
        b = CustomList([4, 5])
        result = a + b

        expected_str = "элементы: [5, 7, 3], сумма: 15"
        self.assertEqual(str(result), expected_str)

        self.assertEqual(sum(result), 15)

    def test_empty_and_single_element_edge_cases(self):
        """крайние случаи с пустыми и одноэлементными списками"""
        a = CustomList([1, 2, 3])
        result = a + 0
        self.assertEqual(list(result), [1, 2, 3])

        result = a + (-1)
        self.assertEqual(list(result), [0, 1, 2])

        result = a - (-1)
        self.assertEqual(list(result), [2, 3, 4])

    def test_type_preservation_in_all_operations(self):
        """проверка сохранения типа CustomList во всех операциях"""
        a = CustomList([1, 2])

        result = a + [3, 4]
        self.assertIsInstance(result, CustomList)

        result = [3, 4] + a
        self.assertIsInstance(result, CustomList)

        b = CustomList([3, 4])
        result = a + b
        self.assertIsInstance(result, CustomList)

        result = a + 5
        self.assertIsInstance(result, CustomList)

        result = 5 + a
        self.assertIsInstance(result, CustomList)

        result = a - [3, 4]
        self.assertIsInstance(result, CustomList)

        result = [3, 4] - a
        self.assertIsInstance(result, CustomList)

    def test_operation_chain_immutability(self):
        """Проверка цепочки операций и неизменности исходных данных"""
        a = CustomList([1, 2, 3])
        b = CustomList([4, 5])
        c = [6, 7, 8, 9]

        result = ((a + b) - c) + 10

        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [4, 5])
        self.assertEqual(c, [6, 7, 8, 9])

        expected = CustomList([1, 2, 3]) + CustomList([4, 5])
        expected = expected - [6, 7, 8, 9]
        expected = expected + 10

        self.assertEqual(list(result), [9, 10, 5, 1])


if __name__ == "__main__":
    unittest.main()
