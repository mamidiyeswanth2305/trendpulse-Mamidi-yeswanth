from __future__ import annotations
from pathlib import Path
from typing import Optional
import pandas as pd


DATA_DIR = Path("data")
OUTPUT_CSV = DATA_DIR / "trends_clean.csv"


def find_latest_json_file(data_dir: Path) -> Optional[Path]:
    """Return the newest trends JSON file from the data folder."""
    json_files = sorted(data_dir.glob("trends_*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if json_files:
        return json_files[0]
    return None


def main() -> None:
    input_file = find_latest_json_file(DATA_DIR)
    if input_file is None:
        print("No Task 1 JSON file found in data/.")
        return

    # Load the raw JSON created in Task 1.
    frame = pd.read_json(input_file)
    print(f"Loaded {len(frame)} stories from {input_file.as_posix()}")

    # Remove duplicate stories based on the unique post ID.
    frame = frame.drop_duplicates(subset=["post_id"])
    print(f"After removing duplicates: {len(frame)}")

    # Drop rows that are missing the core fields required for analysis.
    frame = frame.dropna(subset=["post_id", "title", "score"])
    print(f"After removing nulls: {len(frame)}")

    # Normalize text values and numeric columns before the final quality filter.
    frame["title"] = frame["title"].astype(str).str.strip()
    frame["score"] = pd.to_numeric(frame["score"], errors="coerce")
    frame["num_comments"] = pd.to_numeric(frame["num_comments"], errors="coerce").fillna(0)

    # Remove low-quality stories.
    frame = frame.dropna(subset=["score"])
    frame = frame[frame["score"] >= 5]
    print(f"After removing low scores: {len(frame)}")

    # Make sure the count columns are stored as integers in the final CSV.
    frame["score"] = frame["score"].astype(int)
    frame["num_comments"] = frame["num_comments"].astype(int)

    DATA_DIR.mkdir(exist_ok=True)
    frame.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved {len(frame)} rows to {OUTPUT_CSV.as_posix()}")

    print("\nStories per category:")
    category_counts = frame["category"].value_counts().sort_index()
    for category, count in category_counts.items():
        print(f"  {category:<16}{count}")


if __name__ == "__main__":
    main()
