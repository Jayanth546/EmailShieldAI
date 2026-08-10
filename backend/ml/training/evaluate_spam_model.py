from pathlib import Path

import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "ml" / "data" / "emails.csv"
MODEL_PATH = BASE_DIR / "ml" / "models" / "spam_model.joblib"
OUTPUT_DIR = BASE_DIR / "ml" / "evaluation"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("\n==============================")
    print("SPAM MODEL EVALUATION")
    print("==============================")

    print(f"\nAccuracy: {accuracy:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    # Confusion matrix
    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=["ham", "spam"],
    )

    print("Confusion Matrix:")
    print(matrix)

    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=["Ham", "Spam"],
    )

    display.plot()

    plt.title("EmailShieldAI - Spam Detection Confusion Matrix")
    plt.tight_layout()

    output_path = OUTPUT_DIR / "confusion_matrix.png"

    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"\nConfusion matrix saved to:")
    print(output_path)


if __name__ == "__main__":
    main()
