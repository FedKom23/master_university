import unittest
from custom_metaclass import CustomClass


class TestCustomMeta(unittest.TestCase):
    def test_class_attribute_replacement(self):
        """проверка атрибутов класса"""
        self.assertEqual(CustomClass.custom_x, 50)
        self.assertEqual(CustomClass.custom__z, 50)
        with self.assertRaises(AttributeError):
            _ = CustomClass.x

        with self.assertRaises(AttributeError):
            _ = CustomClass._z

    def test_instance_attributes_renamed(self):
        """тестирование переименования атрибутов экземпляра"""
        inst = CustomClass()
        self.assertEqual(inst.custom_val, 99)
        with self.assertRaises(AttributeError):
            _ = inst.val

    def test_instance_methods_renamed(self):
        """тестирование переименования методов экземпляра"""
        inst = CustomClass()
        self.assertEqual(inst.custom_line(), 100)
        with self.assertRaises(AttributeError):
            _ = inst.line()

    def test_magic_methods_preserved(self):
        """проверка сохранения магических методов"""
        inst = CustomClass()
        self.assertEqual(str(inst), "Custom_by_metaclass")
        self.assertTrue(hasattr(inst, '__str__'))
        self.assertFalse(hasattr(inst, 'custom___str__'))

    def test_dynamic_attributes(self):
        """проверка динамического добавления атрибутов"""
        inst = CustomClass()
        inst.dynamic = "added later"
        self.assertEqual(inst.custom_dynamic, "added later")
        with self.assertRaises(AttributeError):
            _ = inst.dynamic

    def test_multiple_instances(self):
        """тестирование работы с несколькими экземплярами"""
        inst1 = CustomClass(100)
        inst2 = CustomClass(200)

        self.assertEqual(inst1.custom_val, 100)
        self.assertEqual(inst2.custom_val, 200)
        self.assertEqual(inst1.custom_x, 50)
        self.assertEqual(inst2.custom_x, 50)
        inst1.attr1 = "value1"
        inst2.attr2 = "value2"

        self.assertEqual(inst1.custom_attr1, "value1")
        self.assertEqual(inst2.custom_attr2, "value2")
        with self.assertRaises(AttributeError):
            _ = inst1.custom_attr2
        with self.assertRaises(AttributeError):
            _ = inst2.custom_attr1

    def test_nonexistent_attributes(self):
        """проверка несуществующих атрибутов"""
        inst = CustomClass()
        with self.assertRaises(AttributeError):
            _ = inst.yyy


if __name__ == "__main__":
    unittest.main()
