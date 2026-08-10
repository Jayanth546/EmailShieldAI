from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "ml" / "data" / "emails.csv"
MODEL_PATH = BASE_DIR / "ml" / "models" / "spam_model.joblib"


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

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print("Loading trained model...")

    model = joblib.load(MODEL_PATH)

    # Get probability of the spam class.
    probabilities = model.predict_proba(X_test)

    spam_index = list(model.classes_).index("spam")
    spam_probabilities = probabilities[:, spam_index]

    print("\n==============================")
    print("SPAM THRESHOLD ANALYSIS")
    print("==============================")

    print(f"\nTest samples: {len(X_test)}")

    print("\nThreshold Results:")
    print(
        f"{'Threshold':<12}"
        f"{'Accuracy':<12}"
        f"{'Precision':<12}"
        f"{'Recall':<12}"
        f"{'F1':<12}"
        f"{'FP':<8}"
        f"{'FN':<8}"
    )

    print("-" * 72)

    thresholds = [
        0.30,
        0.40,
        0.50,
        0.60,
        0.70,
        0.80,
        0.90,
    ]

    for threshold in thresholds:
        predictions = [
            "spam" if probability >= threshold else "ham"
            for probability in spam_probabilities
        ]

        accuracy = accuracy_score(y_test, predictions)

        precision = precision_score(
            y_test,
            predictions,
            pos_label="spam",
            zero_division=0,
        )

        recall = recall_score(
            y_test,
            predictions,
            pos_label="spam",
            zero_division=0,
        )

        f1 = f1_score(
            y_test,
            predictions,
            pos_label="spam",
            zero_division=0,
        )

        false_positives = sum(
            actual == "ham" and predicted == "spam"
            for actual, predicted in zip(y_test, predictions)
        )

        false_negatives = sum(
            actual == "spam" and predicted == "ham"
            for actual, predicted in zip(y_test, predictions)
        )

        print(
            f"{threshold:<12.2f}"
            f"{accuracy:<12.4f}"
            f"{precision:<12.4f}"
            f"{recall:<12.4f}"
            f"{f1:<12.4f}"
            f"{false_positives:<8}"
            f"{false_negatives:<8}"
        )

    print("\nAnalysis completed.")


if __name__ == "__main__":
    main()
