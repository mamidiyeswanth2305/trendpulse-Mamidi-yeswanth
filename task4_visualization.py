from __future__ import annotations
from pathlib import Path
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


INPUT_CSV = Path("data") / "trends_analysed.csv"
OUTPUT_DIR = Path("outputs")


def shorten_title(title: str, max_length: int = 50) -> str:
    """Shorten long story titles so the chart stays readable."""
    if len(title) <= max_length:
        return title
    return title[: max_length - 3].rstrip() + "..."


def prepare_output_dir() -> None:
    """Create the outputs directory before saving any figures."""
    OUTPUT_DIR.mkdir(exist_ok=True)


def load_data() -> pd.DataFrame:
    """Load the analysed CSV created in Task 3."""
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_CSV.as_posix()}")
    return pd.read_csv(INPUT_CSV)


def save_chart1(frame: pd.DataFrame) -> None:
    """Save a horizontal bar chart for the top 10 stories by score."""
    top_stories = frame.nlargest(10, "score").copy()
    top_stories["short_title"] = top_stories["title"].astype(str).apply(shorten_title)
    top_stories = top_stories.sort_values("score", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_stories["short_title"], top_stories["score"], color="#2a9d8f")
    ax.set_title("Top 10 Stories by Score")
    ax.set_xlabel("Score")
    ax.set_ylabel("Story Title")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "chart1_top_stories.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def save_chart2(frame: pd.DataFrame) -> None:
    """Save a category count bar chart using a different color for each bar."""
    category_counts = frame["category"].value_counts().sort_index()
    colors = ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.bar(category_counts.index, category_counts.values, color=colors[: len(category_counts)])
    ax.set_title("Stories per Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of Stories")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "chart2_categories.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def save_chart3(frame: pd.DataFrame) -> None:
    """Save a scatter plot comparing score and comments by popularity."""
    fig, ax = plt.subplots(figsize=(9, 6))

    popular = frame[frame["is_popular"]]
    not_popular = frame[~frame["is_popular"]]

    ax.scatter(not_popular["score"], not_popular["num_comments"], alpha=0.7, label="Not popular", color="#6c757d")
    ax.scatter(popular["score"], popular["num_comments"], alpha=0.8, label="Popular", color="#d62828")
    ax.set_title("Score vs Comments")
    ax.set_xlabel("Score")
    ax.set_ylabel("Number of Comments")
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "chart3_scatter.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def save_dashboard(frame: pd.DataFrame) -> None:
    """Combine the three charts into one dashboard figure."""
    top_stories = frame.nlargest(10, "score").copy()
    top_stories["short_title"] = top_stories["title"].astype(str).apply(shorten_title)
    top_stories = top_stories.sort_values("score", ascending=True)

    category_counts = frame["category"].value_counts().sort_index()
    colors = ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"]

    popular = frame[frame["is_popular"]]
    not_popular = frame[~frame["is_popular"]]

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("TrendPulse Dashboard", fontsize=18, fontweight="bold")

    axes[0, 0].barh(top_stories["short_title"], top_stories["score"], color="#2a9d8f")
    axes[0, 0].set_title("Top 10 Stories by Score")
    axes[0, 0].set_xlabel("Score")
    axes[0, 0].set_ylabel("Story Title")

    axes[0, 1].bar(category_counts.index, category_counts.values, color=colors[: len(category_counts)])
    axes[0, 1].set_title("Stories per Category")
    axes[0, 1].set_xlabel("Category")
    axes[0, 1].set_ylabel("Number of Stories")

    axes[1, 0].scatter(not_popular["score"], not_popular["num_comments"], alpha=0.7, label="Not popular", color="#6c757d")
    axes[1, 0].scatter(popular["score"], popular["num_comments"], alpha=0.8, label="Popular", color="#d62828")
    axes[1, 0].set_title("Score vs Comments")
    axes[1, 0].set_xlabel("Score")
    axes[1, 0].set_ylabel("Number of Comments")
    axes[1, 0].legend()

    axes[1, 1].axis("off")
    axes[1, 1].text(
        0.5,
        0.6,
        f"Stories analyzed: {len(frame)}\n\nPopular stories: {int(frame['is_popular'].sum())}\nNon-popular stories: {int((~frame['is_popular']).sum())}",
        ha="center",
        va="center",
        fontsize=12,
        bbox={"facecolor": "white", "edgecolor": "#cccccc", "boxstyle": "round,pad=0.5"},
    )

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(OUTPUT_DIR / "dashboard.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    # Load the analysed data from Task 3 and prepare the output folder.
    prepare_output_dir()
    frame = load_data()

    # Save each chart before any display call, as required.
    save_chart1(frame)
    save_chart2(frame)
    save_chart3(frame)
    save_dashboard(frame)

    print("Saved chart1_top_stories.png")
    print("Saved chart2_categories.png")
    print("Saved chart3_scatter.png")
    print("Saved dashboard.png")


if __name__ == "__main__":
    main()
