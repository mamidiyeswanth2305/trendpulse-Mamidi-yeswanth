from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd


INPUT_CSV = Path("data") / "trends_clean.csv"
OUTPUT_CSV = Path("data") / "trends_analysed.csv"


def main() -> None:
    if not INPUT_CSV.exists():
        print(f"Missing input file: {INPUT_CSV.as_posix()}")
        return

    # Load the cleaned data from Task 2.
    frame = pd.read_csv(INPUT_CSV)
    print(f"Loaded data: {frame.shape}")
    print("\nFirst 5 rows:")
    print(frame.head())

    # Basic Pandas exploration.
    average_score = frame["score"].mean()
    average_comments = frame["num_comments"].mean()
    print(f"\nAverage score   : {average_score:.2f}")
    print(f"Average comments: {average_comments:.2f}")

    # Use NumPy for the requested summary statistics.
    score_values = frame["score"].to_numpy()
    comment_values = frame["num_comments"].to_numpy()

    print("\n--- NumPy Stats ---")
    print(f"Mean score   : {np.mean(score_values):.2f}")
    print(f"Median score : {np.median(score_values):.2f}")
    print(f"Std deviation: {np.std(score_values):.2f}")
    print(f"Max score    : {np.max(score_values)}")
    print(f"Min score    : {np.min(score_values)}")

    category_counts = frame["category"].value_counts()
    if not category_counts.empty:
        top_category = category_counts.idxmax()
        top_category_count = int(category_counts.max())
        print(f"\nMost stories in: {top_category} ({top_category_count} stories)")

    most_commented_index = int(np.argmax(comment_values))
    most_commented_story = frame.iloc[most_commented_index]
    print(
        f'\nMost commented story: "{most_commented_story["title"]}" '
        f'-- {int(most_commented_story["num_comments"])} comments'
    )

    # Add the two derived columns requested for Task 4.
    frame["engagement"] = frame["num_comments"] / (frame["score"] + 1)
    frame["is_popular"] = frame["score"] > average_score

    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    frame.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved to {OUTPUT_CSV.as_posix()}")


if __name__ == "__main__":
    main()
