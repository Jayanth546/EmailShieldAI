from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "ml" / "data" / "emails.csv"

REQUIRED_COLUMNS = {"label", "text"}
VALID_LABELS = {"ham", "spam"}


def main():
    print("Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    print(f"Dataset: {DATA_PATH}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    # Check required columns
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Check missing values
    missing_labels = int(df["label"].isna().sum())
    missing_text = int(df["text"].isna().sum())

    if missing_labels:
        raise ValueError(
            f"Dataset contains {missing_labels} missing labels"
        )

    if missing_text:
        raise ValueError(
            f"Dataset contains {missing_text} missing email texts"
        )

    # Check empty text
    empty_text = int(
        df["text"].astype(str).str.strip().eq("").sum()
    )

    if empty_text:
        raise ValueError(
            f"Dataset contains {empty_text} empty email texts"
        )

    # Normalize labels for validation
    labels = (
        df["label"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    invalid_labels = sorted(
        set(labels) - VALID_LABELS
    )

    if invalid_labels:
        raise ValueError(
            f"Invalid labels found: {invalid_labels}. "
            f"Expected only: {sorted(VALID_LABELS)}"
        )

    # Duplicate detection
    duplicate_count = int(
        df.duplicated(subset=["label", "text"]).sum()
    )

    # Class distribution
    class_counts = labels.value_counts()

    print("\nDataset validation")
    print("==================")
    print("Status: VALID")

    print("\nClass distribution:")
    for label in sorted(VALID_LABELS):
        print(
            f"{label}: "
            f"{int(class_counts.get(label, 0))}"
        )

    print(f"\nDuplicate rows: {duplicate_count}")

    if len(class_counts) != 2:
        raise ValueError(
            "Dataset must contain both ham and spam classes"
        )

    print("\nDataset validation completed successfully.")


if __name__ == "__main__":
    main()
