from __future__ import annotations
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests


BASE_URL = "https://hacker-news.firebaseio.com/v0"
HEADERS = {"User-Agent": "TrendPulse/1.0"}
CATEGORY_KEYWORDS = {
	"technology": ["AI", "software", "tech", "code", "computer", "data", "cloud", "API", "GPU", "LLM"],
	"worldnews": ["war", "government", "country", "president", "election", "climate", "attack", "global"],
	"sports": ["NFL", "NBA", "FIFA", "sport", "game", "team", "player", "league", "championship"],
	"science": ["research", "study", "space", "physics", "biology", "discovery", "NASA", "genome"],
	"entertainment": ["movie", "film", "music", "Netflix", "game", "book", "show", "award", "streaming"],
}


def fetch_json(url: str) -> Optional[Any]:
	"""Fetch JSON data and keep the script running if a request fails."""
	try:
		response = requests.get(url, headers=HEADERS, timeout=15)
		response.raise_for_status()
		return response.json()
	except requests.RequestException as exc:
		print(f"Request failed for {url}: {exc}")
	except ValueError as exc:
		print(f"Invalid JSON from {url}: {exc}")
	return None


def fetch_story(story_id: int) -> Optional[Dict[str, Any]]:
	"""Fetch a single HackerNews story by ID."""
	data = fetch_json(f"{BASE_URL}/item/{story_id}.json")
	if isinstance(data, dict):
		return data
	return None


def detect_categories(title: str) -> List[str]:
	"""Return all categories matched by title keywords (case-insensitive)."""
	title_lower = title.lower()
	matched_categories: List[str] = []
	for category, keywords in CATEGORY_KEYWORDS.items():
		if any(keyword.lower() in title_lower for keyword in keywords):
			matched_categories.append(category)
	return matched_categories


def build_story_record(story: Dict[str, Any], category: str) -> Dict[str, Any]:
	"""Extract the required fields into the submission format."""
	return {
		"post_id": story.get("id"),
		"title": story.get("title", ""),
		"category": category,
		"score": story.get("score", 0),
		"num_comments": story.get("descendants", 0),
		"author": story.get("by", ""),
		"collected_at": datetime.now().isoformat(timespec="seconds"),
	}


def main() -> None:
	# Step 1: fetch the top story IDs once.
	top_story_ids = fetch_json(f"{BASE_URL}/topstories.json")
	if not isinstance(top_story_ids, list):
		print("Could not load top stories from HackerNews.")
		return

	top_story_ids = top_story_ids[:500]

	# Step 2: fetch each story's details and assign matching categories.
	categorized_stories: Dict[str, List[Dict[str, Any]]] = {category: [] for category in CATEGORY_KEYWORDS}
	seen_story_ids_by_category = {category: set() for category in CATEGORY_KEYWORDS}

	for story_id in top_story_ids:
		if all(len(categorized_stories[category]) >= 25 for category in CATEGORY_KEYWORDS):
			break

		story = fetch_story(int(story_id))
		if not story:
			continue

		title = story.get("title")
		if not isinstance(title, str) or not title.strip():
			continue

		matched_categories = detect_categories(title)
		if not matched_categories:
			continue

		story_unique_id = story.get("id")
		for category in matched_categories:
			if len(categorized_stories[category]) >= 25:
				continue
			if story_unique_id in seen_story_ids_by_category[category]:
				continue

			categorized_stories[category].append(build_story_record(story, category))
			seen_story_ids_by_category[category].add(story_unique_id)

	# Step 3: keep up to 25 stories per category, then pause once per category loop.
	selected_stories: List[Dict[str, Any]] = []
	for category in CATEGORY_KEYWORDS:
		selected_stories.extend(categorized_stories[category][:25])
		time.sleep(2)

	output_dir = Path("data")
	output_dir.mkdir(exist_ok=True)

	output_path = output_dir / f"trends_{datetime.now().strftime('%Y%m%d')}.json"
	with output_path.open("w", encoding="utf-8") as file_handle:
		json.dump(selected_stories, file_handle, indent=2, ensure_ascii=False)

	print(f"Collected {len(selected_stories)} stories. Saved to {output_path.as_posix()}")


if __name__ == "__main__":
	main()
