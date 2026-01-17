"""Task 1 module."""


class SomeModel:  # pylint: disable=too-few-public-methods
    """Model class."""

    def predict(self, message: str) -> float:  # pylint: disable=unused-argument
        """Predict method."""
        return 0.5


def predict_message_mood(
    message: str,
    bad_thresholds: float = 0.3,
    good_thresholds: float = 0.8,
) -> str:
    """Predict message mood."""
    model = SomeModel()
    score = model.predict(message)

    if score < bad_thresholds:
        return "неуд"
    if score > good_thresholds:
        return "отл"
    return "норм"
