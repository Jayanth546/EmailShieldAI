from pathlib import Path

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "ml" / "data" / "emails.csv"


def main():
    print("Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    if "label" not in df.columns or "text" not in df.columns:
        raise ValueError(
            "Dataset must contain 'label' and 'text' columns"
        )

    df = df.dropna(subset=["label", "text"])

    X = df["text"]
    y = df["label"]

    print(f"Dataset size: {len(df)}")
    print(f"Class distribution:\n{y.value_counts()}")

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

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    scoring = {
        "accuracy": "accuracy",
        "precision": "precision_macro",
        "recall": "recall_macro",
        "f1": "f1_macro",
    }

    print("\nRunning 5-fold cross-validation...")

    results = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=scoring,
    )

    print("\n==============================")
    print("5-FOLD CROSS-VALIDATION")
    print("==============================")

    for metric in scoring:
        scores = results[f"test_{metric}"]

        print(f"\n{metric.upper()}")
        print("Fold scores:", [round(score, 4) for score in scores])
        print(f"Mean: {scores.mean():.4f}")
        print(f"Std:  {scores.std():.4f}")


if __name__ == "__main__":
    main()
