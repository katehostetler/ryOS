#!/usr/bin/env python3
"""
Analyze sentiment of blog posts using TextBlob.
Updates mood data with sentiment scores.
"""

import json
from pathlib import Path

from textblob import TextBlob

def analyze_sentiment(text):
    """Analyze sentiment of text and return polarity score."""
    blob = TextBlob(text)
    return blob.sentiment.polarity

def get_mood_label(score):
    """Map sentiment score to mood label."""
    if score > 0.1:
        return "confident"
    elif score < -0.1:
        return "defensive"
    else:
        return "cautious"

def update_mood_file(filepath):
    """Update a mood file with sentiment analysis."""
    try:
        with open(filepath) as f:
            data = json.load(f)

        if not data.get("posts"):
            print(f"No posts to analyze in {filepath.name}")
            return

        # Analyze each post
        scores = []
        for post in data["posts"]:
            text = f"{post.get('title', '')} {post.get('summary', '')}"
            if text.strip():
                score = analyze_sentiment(text)
                post["sentiment"] = round(score, 3)
                scores.append(score)

        # Calculate average sentiment
        if scores:
            avg_score = sum(scores) / len(scores)
            data["sentiment"] = {
                "score": round(avg_score, 3),
                "label": get_mood_label(avg_score),
            }

            # Update history (keep last 30 data points)
            history = data.get("history", [])
            history.append(round(avg_score, 3))
            data["history"] = history[-30:]

        # Save updated data
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        company = data.get("company", filepath.stem)
        print(f"Updated {company}: score={data['sentiment']['score']:.3f}, label={data['sentiment']['label']}")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    """Main function to analyze sentiment for all mood files."""
    script_dir = Path(__file__).parent.parent
    mood_dir = script_dir / "data" / "mood"

    if not mood_dir.exists():
        print(f"Mood directory not found: {mood_dir}")
        return

    print("Analyzing sentiment...")

    for filepath in mood_dir.glob("*.json"):
        update_mood_file(filepath)

    print("Sentiment analysis complete!")

if __name__ == "__main__":
    main()
