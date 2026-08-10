from pathlib import Path

import joblib


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "spam_model.joblib"
)


class SpamPredictor:
    """
    Machine-learning spam predictor.

    The spam classification threshold is configurable.
    Based on cross-validation of the current dataset,
    the default threshold is 0.50.
    """

    DEFAULT_THRESHOLD = 0.50

    def __init__(
        self,
        model_path=MODEL_PATH,
        threshold=DEFAULT_THRESHOLD,
    ):
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Spam model not found: {self.model_path}"
            )

        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "Spam threshold must be between 0.0 and 1.0"
            )

        self.threshold = float(threshold)

        self.model = joblib.load(
            self.model_path
        )

    def predict(self, text: str) -> dict:
        """
        Predict whether an email is spam.

        Classification is based on the configured
        spam probability threshold.
        """

        if not isinstance(text, str):
            raise TypeError(
                "Email text must be a string"
            )

        text = text.strip()

        # Empty email body
        if not text:
            return {
                "label": "ham",
                "spam_probability": 0.0,
                "ham_probability": 1.0,
            }

        # Get probabilities from the trained model
        probabilities = self.model.predict_proba(
            [text]
        )[0]

        classes = self.model.classes_

        probability_map = dict(
            zip(
                classes,
                probabilities,
            )
        )

        spam_probability = float(
            probability_map.get(
                "spam",
                0.0,
            )
        )

        ham_probability = float(
            probability_map.get(
                "ham",
                0.0,
            )
        )

        # -----------------------------------------
        # Apply configured spam threshold
        # -----------------------------------------
        if spam_probability >= self.threshold:
            label = "spam"
        else:
            label = "ham"

        return {
            "label": label,
            "spam_probability": round(
                spam_probability,
                4,
            ),
            "ham_probability": round(
                ham_probability,
                4,
            ),
        }

