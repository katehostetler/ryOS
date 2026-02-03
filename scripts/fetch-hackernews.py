#!/usr/bin/env python3
"""
Fetch HackerNews data for AI companies using the Algolia HN Search API.
Tracks story count, total points, frontpage hits, and calculates sentiment.
Outputs to data/buzz/hackernews.json
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode, quote_plus

# Search terms for each company
COMPANY_SEARCH_TERMS = {
    "anthropic": ["anthropic", "claude ai", "claude 3", "claude opus", "claude sonnet", "claude haiku"],
    "openai": ["openai", "chatgpt", "gpt-4", "gpt-5", "dall-e", "sora openai"],
    "google": ["google deepmind", "gemini ai", "google ai", "bard google", "gemini pro", "gemini ultra"],
    "meta": ["meta ai", "llama 2", "llama 3", "meta llama", "facebook ai"],
}

# Positive/negative word lists for simple sentiment
POSITIVE_WORDS = [
    "amazing", "awesome", "best", "brilliant", "breakthrough", "excellent",
    "fantastic", "great", "impressive", "incredible", "innovative", "love",
    "revolutionary", "superb", "wonderful", "exciting", "powerful", "fast",
    "better", "improved", "success", "winning", "leading", "advanced"
]

NEGATIVE_WORDS = [
    "bad", "broken", "bug", "crash", "disappointing", "fail", "failure",
    "hate", "horrible", "issue", "leak", "lawsuit", "problem", "scam",
    "slow", "terrible", "unsafe", "vulnerability", "warning", "worse",
    "concern", "dangerous", "risk", "scary", "worried", "layoff", "fired"
]


def fetch_hn_search(query, days_back=7):
    """
    Fetch stories from HN Algolia API for a given query.
    Returns list of story objects.
    """
    # Calculate timestamp for N days ago
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    cutoff_timestamp = int(cutoff_date.timestamp())

    # Build API URL
    params = {
        "query": query,
        "tags": "story",
        "numericFilters": f"created_at_i>{cutoff_timestamp}",
        "hitsPerPage": 100,
    }
    url = f"https://hn.algolia.com/api/v1/search?{urlencode(params, quote_via=quote_plus)}"

    try:
        with urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data.get("hits", [])
    except Exception as e:
        print(f"Error fetching HN data for '{query}': {e}")
        return []


def calculate_title_sentiment(title):
    """
    Calculate a simple sentiment score for a title.
    Returns a value between -1 (negative) and 1 (positive).
    """
    if not title:
        return 0.0

    title_lower = title.lower()
    words = re.findall(r'\b\w+\b', title_lower)

    positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
    negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)

    total = positive_count + negative_count
    if total == 0:
        return 0.0

    return (positive_count - negative_count) / total


def fetch_company_data(company_id, search_terms, days_back=7):
    """
    Fetch and aggregate HN data for a company across all search terms.
    """
    all_stories = {}  # Use dict to dedupe by objectID

    for term in search_terms:
        stories = fetch_hn_search(term, days_back)
        for story in stories:
            story_id = story.get("objectID")
            if story_id and story_id not in all_stories:
                all_stories[story_id] = story

    # Aggregate metrics
    stories_list = list(all_stories.values())
    total_points = sum(s.get("points", 0) or 0 for s in stories_list)
    total_comments = sum(s.get("num_comments", 0) or 0 for s in stories_list)

    # Count frontpage hits (stories with >100 points typically hit front page)
    frontpage_hits = sum(1 for s in stories_list if (s.get("points", 0) or 0) >= 100)

    # Calculate average sentiment from titles
    sentiments = [calculate_title_sentiment(s.get("title", "")) for s in stories_list]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

    # Get top stories for reference
    top_stories = sorted(
        stories_list,
        key=lambda s: (s.get("points", 0) or 0),
        reverse=True
    )[:5]

    return {
        "stories_7d": len(stories_list),
        "total_points": total_points,
        "total_comments": total_comments,
        "frontpage_hits": frontpage_hits,
        "sentiment": round(avg_sentiment, 3),
        "top_stories": [
            {
                "title": s.get("title", ""),
                "url": s.get("url") or f"https://news.ycombinator.com/item?id={s.get('objectID')}",
                "points": s.get("points", 0),
                "comments": s.get("num_comments", 0),
            }
            for s in top_stories
        ],
    }


def main():
    """Fetch HN data for all companies and save to JSON."""
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / "public" / "data" / "buzz"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Also create in data/ for local access
    local_output_dir = script_dir / "data" / "buzz"
    local_output_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching HackerNews data...")

    companies_data = {}
    for company_id, search_terms in COMPANY_SEARCH_TERMS.items():
        print(f"  Fetching data for {company_id}...")
        companies_data[company_id] = fetch_company_data(company_id, search_terms)
        print(f"    Found {companies_data[company_id]['stories_7d']} stories, "
              f"{companies_data[company_id]['total_points']} points")

    result = {
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "companies": companies_data,
    }

    # Save to both locations
    for output_path in [output_dir / "hackernews.json", local_output_dir / "hackernews.json"]:
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Saved HN data to {output_path}")

    print("HackerNews data fetch complete!")


if __name__ == "__main__":
    main()
