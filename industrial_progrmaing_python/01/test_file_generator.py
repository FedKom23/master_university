"""Test task 2 module."""
import io
import unittest
from unittest import mock
from file_generator import file_generator


class TestFileGenerator(unittest.TestCase):
    """Test class."""

    def test_search_with_important_words(self):
        """поиск нужных строк со словами"""
        mock_file_txt = "hello world\npython programming\njava code\n"

        with mock.patch("builtins.open",
                        mock.mock_open(read_data=mock_file_txt)):
            result = list(file_generator(
                "test.txt", ["hello", "python"], []
            ))

            self.assertEqual(result, ["hello world\n", "python programming\n"])

    def test_ignore_lines_with_stop_word(self):
        """игнорирование строк с стоп словом"""
        mock_file_txt = "hello world\nbad word here\ngood line\n"

        with mock.patch("builtins.open",
                        mock.mock_open(read_data=mock_file_txt)):
            result = list(file_generator(
                "test.txt", ["hello", "good"], ["bad"]
            ))

            self.assertEqual(result, ["hello world\n", "good line\n"])

    def test_case_insensitivity(self):
        """проверка регистров в массивах стоп слов и в самом тексте"""
        mock_file_txt = "HELLO world\nPython PROGRAMMING\n"

        with mock.patch("builtins.open",
                        mock.mock_open(read_data=mock_file_txt)):
            result1 = list(file_generator(
                "test.txt", ["hello", "python"], []
            ))
            result2 = list(file_generator(
                "test.txt", ["HEllo", "python"], []
            ))

            expected = ["HELLO world\n", "Python PROGRAMMING\n"]
            self.assertEqual(result1, expected)
            self.assertEqual(result2, expected)

    def test_multiple_important_words_in_line(self):
        """вывод одной строки с >1 нужным словом"""
        mock_file_txt = "hello python world\njava code\n"

        with mock.patch("builtins.open",
                        mock.mock_open(read_data=mock_file_txt)):
            result = list(file_generator(
                "test.txt", ["hello", "python"], []
            ))

            self.assertEqual(result, ["hello python world\n"])

    def test_stop_word_prevents_adding(self):
        """проверка игнорирования строки с нужным словом из-за стоп слова"""
        mock_file_txt = "hello bad world\ngood line\n"

        with mock.patch("builtins.open",
                        mock.mock_open(read_data=mock_file_txt)):
            result = list(file_generator(
                "test.txt", ["hello", "good"], ["bad"]
            ))

            self.assertEqual(result, ["good line\n"])

    def test_empty_file(self):
        """проверка обработки пустого файла"""
        mock_file_txt = ""

        with mock.patch("builtins.open",
                        mock.mock_open(read_data=mock_file_txt)):
            result = list(file_generator(
                "test.txt", ["hello"], ["bad"]
            ))

            self.assertEqual(result, [])

    def test_empty_word_lists(self):
        """проверка с пустыми массивами нужных и стоп слов"""
        mock_file_txt = "hello world\n"

        with mock.patch("builtins.open",
                        mock.mock_open(read_data=mock_file_txt)):
            result = list(file_generator(
                "test.txt", [], []
            ))
            self.assertEqual(result, [])

            result = list(file_generator("test.txt", ["hello"], []))
            self.assertEqual(result, ["hello world\n"])

    def test_file_not_found(self):
        """проверка несуществующего файла"""
        with mock.patch(
            "builtins.open", side_effect=FileNotFoundError("File not found")
        ):
            with self.assertRaises(FileNotFoundError):
                list(file_generator(
                    "nonexistent.txt", ["hello"], []
                ))

    def test_file_object_instead_of_filename(self):
        """работа напрямую с файловым объектом (StringIO)"""
        mock_file_txt = io.StringIO("apple banana\norange fruit\n")
        result = list(file_generator(mock_file_txt, ["orange"], []))
        self.assertEqual(result, ["orange fruit\n"])

    def test_empty_file_with_stringio(self):
        """генератор на пустом файле"""
        mock_file_txt = io.StringIO("")
        result = list(file_generator(mock_file_txt, ["anything"], []))
        self.assertEqual(result, [])

    def test_match_entire_line(self):
        """строка совпадает целиком со стоп-словом или словом поиска"""
        mock_file_txt = io.StringIO("stop\nword\n")
        result = list(file_generator(mock_file_txt, ["word"],
                                     ["stop", "word"]))
        self.assertEqual(result, [])

    def test_single_character_search(self):
        """поиск одиночного символа"""
        mock_file_txt = io.StringIO("a b c\nalpha beta\n")
        result = list(file_generator(mock_file_txt, ["a"], []))
        self.assertEqual(result, ["a b c\n"])

    def test_partial_word_match(self):
        """частичное совпадение слова"""
        mock_file_txt = io.StringIO("роза красная\nрозовый куст\n")
        result = list(file_generator(mock_file_txt, ["роза"], []))
        self.assertEqual(result, ["роза красная\n"])

    def test_full_string_match(self):
        """полное совпадение строки"""
        mock_file_txt = io.StringIO("роза красная\nрозовый куст\n")
        result = list(file_generator(mock_file_txt,
                                     ["роза", "красная"], []))
        self.assertEqual(result, ["роза красная\n"])

    def test_stop_word_has_priority(self):
        """стоп-слово имеет приоритет над искомым словом"""
        mock_file_txt = io.StringIO("роза красная\n")
        result = list(file_generator(mock_file_txt, ["роза"],
                                     ["красная"]))
        self.assertEqual(result, [])

    def test_exact_match_whole_line_stop_word(self):
        """строка состоит только из стоп-слова"""
        mock_file_txt = io.StringIO("стоп\nнестоп слово\n")
        result = list(file_generator(mock_file_txt, ["слово"], ["стоп"]))
        self.assertEqual(result, ["нестоп слово\n"])

    def test_exact_match_whole_line_search_word(self):
        """строка состоит только из искомого слова"""
        mock_file_txt = io.StringIO("искомое\nдругое слово\n")
        result = list(file_generator(mock_file_txt, ["искомое"], []))
        self.assertEqual(result, ["искомое\n"])

    def test_stop_word_equals_search_word(self):
        """стоп-слово совпадает с искомым словом"""
        mock_file_txt = io.StringIO("конфликт\nдругое слово\n")
        result = list(file_generator(mock_file_txt, ["конфликт"], ["конфликт"]))
        self.assertEqual(result, [])

    def test_single_character_stop_word(self):
        """стоп-слово из одного символа"""
        mock_file_txt = io.StringIO("a b c\nd e f\n")
        result = list(file_generator(mock_file_txt, ["b", "e"], ["a"]))
        self.assertEqual(result, ["d e f\n"])

    def test_single_character_both_lists(self):
        """одиночные символы в обоих списках"""
        mock_file_txt = io.StringIO("x y z\nx\n")
        result = list(file_generator(mock_file_txt, ["y"], ["x"]))
        self.assertEqual(result, [])

    def test_partial_word_stop_word(self):
        """частичное совпадение стоп-слова"""
        mock_file_txt = io.StringIO("розовый куст\nроза красная\n")
        result = list(file_generator(mock_file_txt, ["куст"], ["роз"]))
        self.assertEqual(result, ["розовый куст\n"])

    def test_word_in_different_forms(self):
        """слово в разных формах (падежи, времена)"""
        mock_file_txt = io.StringIO("я бегу\nты бежишь\nон бежит\n")
        result = list(file_generator(mock_file_txt, ["бегу"], []))
        self.assertEqual(result, ["я бегу\n"])

    def test_empty_lines_with_spaces(self):
        """строки только с пробелами и табами"""
        mock_file_txt = io.StringIO("   \n\t\nслово\n")
        result = list(file_generator(mock_file_txt, ["слово"], []))
        self.assertEqual(result, ["слово\n"])

    def test_line_with_only_punctuation(self):
        """строка только со знаками препинания"""
        mock_file_txt = io.StringIO(".,!?\nслово знак.\n")
        result = list(file_generator(mock_file_txt, ["слово"], []))
        self.assertEqual(result, ["слово знак.\n"])

    def test_search_word_with_punctuation(self):
        """искомое слово со знаками препинания в файле"""
        mock_file_txt = io.StringIO("слово, запятая\nслово точка.\n")
        result = list(file_generator(mock_file_txt, ["слово"], []))
        self.assertEqual(result, ['слово, запятая\n', 'слово точка.\n'])


if __name__ == "__main__":
    unittest.main()
