from pathlib import Path

import joblib


BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "ml" / "models" / "spam_model.joblib"


class SpamPredictor:
    def __init__(self, model_path=MODEL_PATH):
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Spam model not found: {self.model_path}"
            )

        self.model = joblib.load(self.model_path)

    def predict(self, text: str) -> dict:
        if not isinstance(text, str):
            raise TypeError("Email text must be a string")

        text = text.strip()

        if not text:
            return {
                "label": "ham",
                "spam_probability": 0.0,
                "ham_probability": 1.0,
            }

        label = self.model.predict([text])[0]

        probabilities = self.model.predict_proba([text])[0]
        classes = self.model.classes_

        probability_map = dict(zip(classes, probabilities))

        spam_probability = float(
            probability_map.get("spam", 0.0)
        )

        ham_probability = float(
            probability_map.get("ham", 0.0)
        )

        return {
            "label": str(label),
            "spam_probability": round(spam_probability, 4),
            "ham_probability": round(ham_probability, 4),
        }
