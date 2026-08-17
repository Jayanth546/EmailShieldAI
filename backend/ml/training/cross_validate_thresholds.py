from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "ml" / "data" / "emails.csv"


THRESHOLDS = [
    0.30,
    0.40,
    0.50,
    0.60,
    0.70,
    0.80,
    0.90,
]


def create_model():
    return Pipeline(
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


def main():
    print("Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    if "label" not in df.columns or "text" not in df.columns:
        raise ValueError(
            "Dataset must contain 'label' and 'text' columns"
        )

    df = df.dropna(
        subset=["label", "text"]
    )

    X = df["text"]
    y = df["label"]

    print(f"Dataset size: {len(df)}")

    print("\nClass distribution:")
    print(y.value_counts())

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    results = {
        threshold: {
            "accuracy": [],
            "precision": [],
            "recall": [],
            "f1": [],
            "fp": [],
            "fn": [],
        }
        for threshold in THRESHOLDS
    }

    print(
        "\nRunning 5-fold threshold cross-validation..."
    )

    for fold, (train_index, test_index) in enumerate(
        cv.split(X, y),
        start=1,
    ):
        print(f"\nFold {fold}")

        X_train = X.iloc[train_index]
        X_test = X.iloc[test_index]

        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        model = create_model()

        model.fit(
            X_train,
            y_train,
        )

        probabilities = model.predict_proba(
            X_test
        )

        spam_index = list(
            model.classes_
        ).index("spam")

        spam_probabilities = probabilities[
            :, spam_index
        ]

        for threshold in THRESHOLDS:

            predictions = [
                "spam"
                if probability >= threshold
                else "ham"
                for probability in spam_probabilities
            ]

            accuracy = accuracy_score(
                y_test,
                predictions,
            )

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
                actual == "ham"
                and predicted == "spam"
                for actual, predicted in zip(
                    y_test,
                    predictions,
                )
            )

            false_negatives = sum(
                actual == "spam"
                and predicted == "ham"
                for actual, predicted in zip(
                    y_test,
                    predictions,
                )
            )

            results[threshold]["accuracy"].append(
                accuracy
            )

            results[threshold]["precision"].append(
                precision
            )

            results[threshold]["recall"].append(
                recall
            )

            results[threshold]["f1"].append(
                f1
            )

            results[threshold]["fp"].append(
                false_positives
            )

            results[threshold]["fn"].append(
                false_negatives
            )

    print("\n")
    print("=" * 86)
    print("CROSS-VALIDATED THRESHOLD RESULTS")
    print("=" * 86)

    print(
        f"{'Threshold':<12}"
        f"{'Accuracy':<14}"
        f"{'Precision':<14}"
        f"{'Recall':<14}"
        f"{'F1':<14}"
        f"{'FP':<8}"
        f"{'FN':<8}"
    )

    print("-" * 86)

    summary = []

    for threshold in THRESHOLDS:

        accuracy_mean = sum(
            results[threshold]["accuracy"]
        ) / len(
            results[threshold]["accuracy"]
        )

        precision_mean = sum(
            results[threshold]["precision"]
        ) / len(
            results[threshold]["precision"]
        )

        recall_mean = sum(
            results[threshold]["recall"]
        ) / len(
            results[threshold]["recall"]
        )

        f1_mean = sum(
            results[threshold]["f1"]
        ) / len(
            results[threshold]["f1"]
        )

        fp_total = sum(
            results[threshold]["fp"]
        )

        fn_total = sum(
            results[threshold]["fn"]
        )

        summary.append(
            {
                "threshold": threshold,
                "accuracy": accuracy_mean,
                "precision": precision_mean,
                "recall": recall_mean,
                "f1": f1_mean,
                "fp": fp_total,
                "fn": fn_total,
            }
        )

        print(
            f"{threshold:<12.2f}"
            f"{accuracy_mean:<14.4f}"
            f"{precision_mean:<14.4f}"
            f"{recall_mean:<14.4f}"
            f"{f1_mean:<14.4f}"
            f"{fp_total:<8}"
            f"{fn_total:<8}"
        )

    best = max(
        summary,
        key=lambda item: item["f1"],
    )

    print("\n")
    print("=" * 50)
    print("BEST CROSS-VALIDATED THRESHOLD")
    print("=" * 50)

    print(
        f"Threshold : {best['threshold']:.2f}"
    )

    print(
        f"Accuracy  : {best['accuracy']:.4f}"
    )

    print(
        f"Precision : {best['precision']:.4f}"
    )

    print(
        f"Recall    : {best['recall']:.4f}"
    )

    print(
        f"F1        : {best['f1']:.4f}"
    )

    print(
        f"False Positives : {best['fp']}"
    )

    print(
        f"False Negatives : {best['fn']}"
    )

    print(
        "\nCross-validation completed."
    )


if __name__ == "__main__":
    main()
