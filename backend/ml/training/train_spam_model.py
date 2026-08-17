from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "ml" / "data" / "emails.csv"
MODEL_PATH = BASE_DIR / "ml" / "models" / "spam_model.joblib"


def main():
    print("Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    if "label" not in df.columns or "text" not in df.columns:
        raise ValueError("Dataset must contain 'label' and 'text' columns")

    df = df.dropna(subset=["label", "text"])

    X = df["text"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                ),
            ),
            (
                "classifier",
                MultinomialNB(),
            ),
        ]
    )

    print("Training model...")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print(f"\nAccuracy: {accuracy:.2f}")
    print("\nClassification report:")
    print(classification_report(y_test, predictions, zero_division=0))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    print(f"\nModel saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
