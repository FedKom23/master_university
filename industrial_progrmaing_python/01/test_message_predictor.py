"""Test task 1 module."""
import unittest
from unittest import mock

from message_predictor import predict_message_mood


class TestPredictMessageMood(unittest.TestCase):
    """Test class."""

    def test_multi_return_thresholds(self):
        """проверка разных трешхолдов в зависимости от сообщения"""
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.side_effect = lambda message: (
                0.1 if message == "Вулкан" else 0.85
            )

            result1 = predict_message_mood("Вулкан")
            result2 = predict_message_mood("Привет")

            self.assertEqual(result1, "неуд")
            self.assertEqual(result2, "отл")

            self.assertEqual(
                [mock.call("Вулкан"), mock.call("Привет")
                 ], mock_predict.mock_calls
            )

    def test_return_custom_bad_threshold(self):
        """проверка установленного bad порога"""
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.side_effect = (
                lambda message: 0.25
            )
            result = predict_message_mood("Сообщение", bad_thresholds=0.4)

            self.assertEqual(result, "неуд")
            self.assertEqual(
                [
                    mock.call("Сообщение"),
                ],
                mock_predict.mock_calls,
            )

    def test_return_custom_good_threshold(self):
        """проверка установленного good порога"""
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.side_effect = lambda message: 0.7

            result = predict_message_mood(
                "Сообщение", good_thresholds=0.6
            )

            self.assertEqual(result, "отл")
            self.assertEqual(
                [
                    mock.call("Сообщение"),
                ],
                mock_predict.mock_calls,
            )

    def test_return_both_custom_thresholds(self):
        """проверка установленного обоих порогов"""
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.side_effect = lambda message: 0.5
            result = predict_message_mood(
                "Сообщение", bad_thresholds=0.4, good_thresholds=0.6
            )

            self.assertEqual(result, "норм")
            self.assertEqual(
                [
                    mock.call("Сообщение"),
                ],
                mock_predict.mock_calls,
            )

    def test_equal_thresholds(self):
        """Проверка точного совпадения с границами"""
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.side_effect = [0.3, 0.8]

            result1 = predict_message_mood(
                "msg", bad_thresholds=0.3, good_thresholds=0.8)
            result2 = predict_message_mood(
                "msg", bad_thresholds=0.3, good_thresholds=0.8)

            self.assertEqual(result1, "норм")
            self.assertEqual(result2, "норм")

    def test_near_thresholds(self):
        """Проверка значений чуть меньше/больше порогов"""
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.side_effect = [0.29, 0.31, 0.79, 0.81]

            res1 = predict_message_mood(
                "msg", bad_thresholds=0.3, good_thresholds=0.8)
            res2 = predict_message_mood(
                "msg", bad_thresholds=0.3, good_thresholds=0.8)
            res3 = predict_message_mood(
                "msg", bad_thresholds=0.3, good_thresholds=0.8)
            res4 = predict_message_mood(
                "msg", bad_thresholds=0.3, good_thresholds=0.8)

            self.assertEqual(res1, "неуд")
            self.assertEqual(res2, "норм")
            self.assertEqual(res3, "норм")
            self.assertEqual(res4, "отл")

    def test_exact_bad_threshold(self):
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.return_value = 0.3

            result = predict_message_mood(
                "Тестовое сообщение", bad_thresholds=0.3, good_thresholds=0.8
            )

            self.assertEqual(result, "норм")
            mock_predict.assert_called_once_with("Тестовое сообщение")

    def test_exact_good_threshold(self):
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.return_value = 0.8

            result = predict_message_mood(
                "Тестовое сообщение", bad_thresholds=0.3, good_thresholds=0.8
            )

            self.assertEqual(result, "норм")
            mock_predict.assert_called_once_with("Тестовое сообщение")

    def test_epsilon_below_bad_threshold(self):
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.return_value = 0.299
            result = predict_message_mood(
                "Сообщение", bad_thresholds=0.3, good_thresholds=0.8
            )

            self.assertEqual(result, "неуд")
            mock_predict.assert_called_once_with("Сообщение")

    def test_epsilon_above_bad_threshold(self):
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.return_value = 0.301

            result = predict_message_mood(
                "Сообщение", bad_thresholds=0.3, good_thresholds=0.8
            )

            self.assertEqual(result, "норм")
            mock_predict.assert_called_once_with("Сообщение")

    def test_epsilon_below_good_threshold(self):
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.return_value = 0.799

            result = predict_message_mood(
                "Сообщение", bad_thresholds=0.3, good_thresholds=0.8
            )

            self.assertEqual(result, "норм")
            mock_predict.assert_called_once_with("Сообщение")

    def test_epsilon_above_good_threshold(self):
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.return_value = 0.801

            result = predict_message_mood(
                "Сообщение", bad_thresholds=0.3, good_thresholds=0.8
            )

            self.assertEqual(result, "отл")
            mock_predict.assert_called_once_with("Сообщение")

    def test_bad_and_good_thresholds_equal(self):
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.side_effect = [0.49, 0.5, 0.51]

            results = []
            for _ in range(3):
                results.append(predict_message_mood(
                    "Сообщение", bad_thresholds=0.5, good_thresholds=0.5
                ))

            self.assertEqual(results[0], "неуд")
            self.assertEqual(results[1], "норм")
            self.assertEqual(results[2], "отл")
            self.assertEqual(mock_predict.call_count, 3)

    def test_custom_thresholds_with_boundaries(self):
        with mock.patch("message_predictor.SomeModel.predict") as mock_predict:
            mock_predict.side_effect = [0.25, 0.25, 0.75, 0.75]

            result1 = predict_message_mood(
                "msg", bad_thresholds=0.25, good_thresholds=0.75
            )
            result2 = predict_message_mood(
                "msg", bad_thresholds=0.26, good_thresholds=0.75
            )
            result3 = predict_message_mood(
                "msg", bad_thresholds=0.25, good_thresholds=0.75
            )
            result4 = predict_message_mood(
                "msg", bad_thresholds=0.25, good_thresholds=0.74
            )

            self.assertEqual(result1, "норм")
            self.assertEqual(result2, "неуд")
            self.assertEqual(result3, "норм")
            self.assertEqual(result4, "отл")


if __name__ == "__main__":
    unittest.main()
