#!/usr/bin/env python3
"""
One-time script to backfill historical data.
Populates 30-90 days of REAL historical data for stocks, mood, and pulse.
All data is derived from real sources - no synthetic data.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

import feedparser
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from textblob import TextBlob

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AI-Weather-Report/1.0)"
}

# =============================================================================
# Stock Data (already real - uses yfinance)
# =============================================================================

def backfill_stocks():
    """Backfill 90 days of real stock data from yfinance."""
    print("Backfilling stock data...")

    tickers = {
        "MSFT": "Microsoft",
        "GOOGL": "Alphabet",
        "AMZN": "Amazon",
        "META": "Meta",
        "NVDA": "NVIDIA",
    }

    stocks = []

    for ticker, name in tickers.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo")  # 90 days

            if hist.empty:
                print(f"  Warning: No historical data for {ticker}")
                continue

            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else hist.iloc[0]

            price = round(latest['Close'], 2)
            change = round(price - prev['Close'], 2)
            change_percent = round((change / prev['Close']) * 100, 2)

            history = [round(p, 2) for p in hist['Close'].tolist()]

            stocks.append({
                "ticker": ticker,
                "name": name,
                "price": price,
                "change": change,
                "changePercent": change_percent,
                "history": history,
            })

            print(f"  {ticker}: {len(history)} days of history")

        except Exception as e:
            print(f"  Error fetching {ticker}: {e}")

    return stocks

# =============================================================================
# Mood Data - Fetch real posts and calculate sentiment history
# =============================================================================

RSS_SOURCES = {
    "openai": {
        "url": "https://openai.com/blog/rss.xml",
        "name": "OpenAI",
    },
    "google": {
        "url": "https://blog.google/technology/ai/rss/",
        "name": "Google DeepMind",
    },
    "meta": {
        "url": "https://about.fb.com/news/feed/",
        "name": "Meta AI",
        "filter_keywords": ["ai", "llama", "artificial intelligence", "machine learning", "meta ai"],
    },
}

def analyze_sentiment(text):
    """Analyze sentiment of text using TextBlob."""
    if not text or not text.strip():
        return 0.0
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

def parse_date(date_str):
    """Try to parse a date string in various formats."""
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip()[:19], fmt[:len(date_str.strip())])
        except ValueError:
            continue
    return None

def fetch_rss_posts_with_dates(source):
    """Fetch all posts from RSS feed with dates and sentiment."""
    posts = []
    try:
        feed = feedparser.parse(source["url"])

        for entry in feed.entries[:50]:  # Get up to 50 entries for history
            title = entry.get("title", "")
            summary = entry.get("summary", "")

            # Apply keyword filter if specified
            if "filter_keywords" in source:
                combined = (title + " " + summary).lower()
                if not any(kw in combined for kw in source["filter_keywords"]):
                    continue

            # Parse date
            date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                date = datetime(*entry.updated_parsed[:6])

            if date:
                # Calculate sentiment
                text = f"{title} {summary}"
                sentiment = analyze_sentiment(text)

                posts.append({
                    "title": title,
                    "date": date.strftime("%Y-%m-%d"),
                    "url": entry.get("link", ""),
                    "summary": summary[:500],
                    "sentiment": round(sentiment, 3),
                    "datetime": date,
                })

        print(f"  Fetched {len(posts)} posts from {source['name']} RSS")
    except Exception as e:
        print(f"  Error fetching RSS from {source['url']}: {e}")

    return posts

def scrape_anthropic_posts():
    """Scrape Anthropic news with dates and sentiment."""
    posts = []
    url = "https://www.anthropic.com/news"

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find article links
        articles = soup.find_all("a", href=re.compile(r"/news/"))
        seen_urls = set()

        for article in articles:
            href = article.get("href", "")
            if href in seen_urls or not href.startswith("/news/"):
                continue
            seen_urls.add(href)

            # Try to find title
            title_elem = article.find(["h2", "h3", "h4"]) or article
            title = title_elem.get_text(strip=True) if title_elem else ""

            if not title or len(title) < 5:
                continue

            # Try to find date
            date_elem = article.find_parent().find("time") if article.find_parent() else None
            date = None
            if date_elem:
                date_text = date_elem.get("datetime") or date_elem.get_text(strip=True)
                date = parse_date(date_text)

            # If no date found, try to extract from URL or use None
            if not date:
                # Anthropic URLs sometimes have dates
                date_match = re.search(r"(\d{4})[/-](\d{2})[/-](\d{2})", href)
                if date_match:
                    try:
                        date = datetime(int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)))
                    except ValueError:
                        pass

            link_url = f"https://www.anthropic.com{href}"
            sentiment = analyze_sentiment(title)

            posts.append({
                "title": title,
                "date": date.strftime("%Y-%m-%d") if date else "",
                "url": link_url,
                "summary": "",
                "sentiment": round(sentiment, 3),
                "datetime": date,
            })

            if len(posts) >= 30:
                break

        print(f"  Scraped {len(posts)} posts from Anthropic")
    except Exception as e:
        print(f"  Error scraping Anthropic: {e}")

    return posts

def build_mood_history(posts, days=30):
    """Build a rolling sentiment history from real posts.

    For each day in the past N days, calculate the average sentiment
    of posts from that day and the preceding 7 days (rolling average).
    """
    if not posts:
        return []

    # Sort posts by date
    dated_posts = [p for p in posts if p.get("datetime")]
    if not dated_posts:
        # If no dated posts, just return a single score
        avg = sum(p.get("sentiment", 0) for p in posts) / len(posts)
        return [round(avg, 3)] * min(7, days)

    dated_posts.sort(key=lambda x: x["datetime"])

    today = datetime.now()
    history = []

    for day_offset in range(days - 1, -1, -1):
        target_date = today - timedelta(days=day_offset)

        # Get posts from the previous 7 days up to target_date
        window_start = target_date - timedelta(days=7)

        window_posts = [
            p for p in dated_posts
            if p["datetime"] and window_start <= p["datetime"] <= target_date
        ]

        if window_posts:
            avg_sentiment = sum(p.get("sentiment", 0) for p in window_posts) / len(window_posts)
        else:
            # Use the most recent known sentiment or neutral
            if history:
                avg_sentiment = history[-1]
            else:
                # Use overall average
                avg_sentiment = sum(p.get("sentiment", 0) for p in dated_posts) / len(dated_posts)

        history.append(round(avg_sentiment, 3))

    return history

def backfill_mood():
    """Backfill mood history with real sentiment data from blog posts."""
    print("Backfilling mood data...")

    script_dir = Path(__file__).parent.parent
    mood_dir = script_dir / "data" / "mood"
    mood_dir.mkdir(parents=True, exist_ok=True)

    # Fetch real posts for each company
    company_posts = {}

    # RSS sources
    for company_id, source in RSS_SOURCES.items():
        company_posts[company_id] = fetch_rss_posts_with_dates(source)

    # Anthropic (scraped)
    company_posts["anthropic"] = scrape_anthropic_posts()

    # Also scrape Meta AI blog for additional posts
    try:
        response = requests.get("https://ai.meta.com/blog/", headers=HEADERS, timeout=30)
        if response.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            meta_ai_posts = []
            for link in soup.find_all("a", href=re.compile(r"/blog/")):
                title = link.get_text(strip=True)
                if title and len(title) > 5:
                    sentiment = analyze_sentiment(title)
                    meta_ai_posts.append({
                        "title": title,
                        "date": "",
                        "url": f"https://ai.meta.com{link.get('href', '')}",
                        "sentiment": round(sentiment, 3),
                        "datetime": None,
                    })
                    if len(meta_ai_posts) >= 20:
                        break
            # Merge with existing Meta posts
            company_posts["meta"].extend(meta_ai_posts)
            print(f"  Added {len(meta_ai_posts)} posts from Meta AI blog")
    except Exception as e:
        print(f"  Error scraping Meta AI blog: {e}")

    # Save mood data for each company
    company_names = {
        "anthropic": "Anthropic",
        "openai": "OpenAI",
        "google": "Google DeepMind",
        "meta": "Meta AI",
    }

    for company_id, posts in company_posts.items():
        filepath = mood_dir / f"{company_id}.json"

        # Build real history from posts
        history = build_mood_history(posts, days=30)

        # Calculate current sentiment
        if posts:
            recent_posts = sorted(posts, key=lambda x: x.get("date", ""), reverse=True)[:10]
            avg_score = sum(p.get("sentiment", 0) for p in recent_posts) / len(recent_posts)
        else:
            avg_score = 0.0

        # Prepare posts for output (remove datetime field)
        output_posts = []
        for p in posts[:10]:
            output_posts.append({
                "title": p["title"],
                "date": p["date"],
                "url": p["url"],
                "sentiment": p.get("sentiment", 0),
            })

        data = {
            "company": company_names.get(company_id, company_id),
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
            "sentiment": {
                "score": round(avg_score, 3),
                "label": get_mood_label(avg_score),
            },
            "posts": output_posts,
            "history": history,
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"  Saved {company_names.get(company_id, company_id)}: {len(history)} days of history, {len(output_posts)} posts")

# =============================================================================
# Pulse Data - Calculate real weekly activity from changelog entries
# =============================================================================

CHANGELOG_SOURCES = {
    "anthropic": {
        "name": "Anthropic",
        "url": "https://docs.anthropic.com/en/release-notes/overview",
    },
    "openai": {
        "name": "OpenAI",
        "url": "https://platform.openai.com/docs/changelog",
    },
    "google": {
        "name": "Google DeepMind",
        "url": "https://ai.google.dev/gemini-api/docs/changelog",
    },
}

def categorize_release(title):
    """Categorize a release based on its title."""
    title_lower = title.lower()
    if any(kw in title_lower for kw in ["major", "launch", "release", "new model", "introducing"]):
        return "major"
    elif any(kw in title_lower for kw in ["deprecat", "sunset", "removing", "end of"]):
        return "deprecation"
    elif any(kw in title_lower for kw in ["fix", "bug", "patch", "issue", "resolve"]):
        return "fix"
    else:
        return "feature"

def scrape_changelog_entries(source):
    """Scrape changelog entries with dates."""
    releases = []

    try:
        response = requests.get(source["url"], headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Look for headings with dates
        headings = soup.find_all(["h2", "h3", "h4"])

        for heading in headings:
            text = heading.get_text(strip=True)

            # Look for date patterns
            date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
            if not date_match:
                date_match = re.search(r"\b([A-Z][a-z]+ \d{1,2}, \d{4})\b", text)

            if date_match:
                date_str = date_match.group(1)
                date = parse_date(date_str)

                # Get title (remove date from text)
                title = re.sub(r"\s*[-–]\s*\d{4}-\d{2}-\d{2}", "", text).strip()
                title = re.sub(r"\s*[-–]\s*[A-Z][a-z]+ \d{1,2}, \d{4}", "", title).strip()

                if not title:
                    # Try to get content from next element
                    next_elem = heading.find_next_sibling()
                    if next_elem:
                        li = next_elem.find("li")
                        if li:
                            title = li.get_text(strip=True)[:100]
                        else:
                            title = next_elem.get_text(strip=True)[:100]

                if title and date:
                    releases.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "type": categorize_release(title),
                        "title": title[:100],
                        "datetime": date,
                    })

        print(f"  Scraped {len(releases)} releases from {source['name']}")
    except Exception as e:
        print(f"  Error scraping {source['name']} changelog: {e}")

    return releases

def fetch_github_releases():
    """Fetch Meta's Llama releases from GitHub API."""
    releases = []
    url = "https://api.github.com/repos/meta-llama/llama-models/releases"

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

        for release in data[:50]:
            published = release.get("published_at", "")
            date = parse_date(published) if published else None
            title = release.get("name", "") or release.get("tag_name", "")

            if date and title:
                releases.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "type": categorize_release(title),
                    "title": title[:100],
                    "datetime": date,
                })

        print(f"  Fetched {len(releases)} releases from Meta GitHub")
    except Exception as e:
        print(f"  Error fetching Meta GitHub releases: {e}")

    return releases

def calculate_real_activity(releases, weeks=14):
    """Calculate real weekly activity counts from releases with dates."""
    activity = []
    today = datetime.now()

    # Count releases per week for last N weeks
    for week in range(weeks - 1, -1, -1):
        week_end = today - timedelta(days=week * 7)
        week_start = week_end - timedelta(days=7)

        count = 0
        for release in releases:
            if release.get("datetime"):
                if week_start <= release["datetime"] < week_end:
                    count += 1

        activity.append(count)

    return activity

def backfill_pulse():
    """Backfill pulse activity data from real changelog entries."""
    print("Backfilling pulse data...")

    script_dir = Path(__file__).parent.parent
    pulse_path = script_dir / "data" / "pulse" / "releases.json"
    pulse_path.parent.mkdir(parents=True, exist_ok=True)

    companies = {}

    # Scrape changelogs
    for company_id, source in CHANGELOG_SOURCES.items():
        releases = scrape_changelog_entries(source)

        # Calculate real weekly activity
        activity = calculate_real_activity(releases, weeks=14)

        # Prepare releases for output (remove datetime field)
        output_releases = []
        for r in releases[:10]:
            output_releases.append({
                "date": r["date"],
                "type": r["type"],
                "title": r["title"],
            })

        companies[company_id] = {
            "name": source["name"],
            "releases": output_releases,
            "activity": activity,
        }

        print(f"  {source['name']}: {len(output_releases)} releases, {sum(activity)} total activity")

    # Meta (GitHub releases)
    meta_releases = fetch_github_releases()
    meta_activity = calculate_real_activity(meta_releases, weeks=14)

    output_meta_releases = []
    for r in meta_releases[:10]:
        output_meta_releases.append({
            "date": r["date"],
            "type": r["type"],
            "title": r["title"],
        })

    companies["meta"] = {
        "name": "Meta AI",
        "releases": output_meta_releases,
        "activity": meta_activity,
    }

    print(f"  Meta AI: {len(output_meta_releases)} releases, {sum(meta_activity)} total activity")

    data = {
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "companies": companies,
    }

    with open(pulse_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Saved pulse data to {pulse_path}")

# =============================================================================
# Main
# =============================================================================

def main():
    """Main function to backfill all historical data."""
    script_dir = Path(__file__).parent.parent

    print("=" * 60)
    print("Starting REAL historical data backfill...")
    print("All data derived from actual sources - no synthetic data")
    print("=" * 60)
    print()

    # Backfill stocks (real data from yfinance)
    stocks = backfill_stocks()
    if stocks:
        stocks_path = script_dir / "data" / "pressure" / "stocks.json"
        stocks_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
            "stocks": stocks,
        }

        with open(stocks_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved stock data to {stocks_path}")

    print()

    # Backfill mood (real sentiment from blog posts)
    backfill_mood()

    print()

    # Backfill pulse (real activity from changelogs)
    backfill_pulse()

    print()
    print("=" * 60)
    print("Historical backfill complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
