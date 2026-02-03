#!/usr/bin/env python3
"""
Fetch changelog/release data for AI companies from their developer docs.
Outputs to data/pulse/releases.json
"""

import json
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Changelog sources
SOURCES = {
    "anthropic": {
        "name": "Anthropic",
        "url": "https://docs.anthropic.com/en/release-notes/overview",
        "type": "scrape",
        "github_url": "https://api.github.com/repos/anthropics/anthropic-sdk-python/releases",
        "github_alt": "https://api.github.com/repos/anthropics/anthropic-sdk-typescript/releases",
    },
    "openai": {
        "name": "OpenAI",
        "url": "https://api.github.com/repos/openai/openai-python/releases",
        "type": "github",  # Changed to use GitHub API for OpenAI Python SDK releases
        "alt_url": "https://api.github.com/repos/openai/openai-node/releases",
    },
    "google": {
        "name": "Google DeepMind",
        "url": "https://ai.google.dev/gemini-api/docs/changelog",
        "type": "scrape",
    },
    "meta": {
        "name": "Meta AI",
        "url": "https://api.github.com/repos/meta-llama/llama/releases",
        "type": "github",
        "alt_url": "https://api.github.com/repos/facebookresearch/llama/releases",
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AI-Weather-Report/1.0)"
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

def parse_date(date_str):
    """Try to parse a date string in various formats."""
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%SZ",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%m/%d/%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return ""

def scrape_anthropic_changelog():
    """Scrape Anthropic's release notes."""
    releases = []

    try:
        response = requests.get(SOURCES["anthropic"]["url"], headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Look for release entries
        entries = soup.find_all(["article", "section", "div"], class_=re.compile(r"release|changelog|update"))

        if not entries:
            # Try finding headings with dates
            headings = soup.find_all(["h2", "h3", "h4"])
            for heading in headings:
                text = heading.get_text(strip=True)
                # Check if heading contains a date-like pattern
                date_match = re.search(r"\b(\d{4}-\d{2}-\d{2}|\w+ \d{1,2}, \d{4})\b", text)
                if date_match:
                    date_str = parse_date(date_match.group(1))
                    title = re.sub(r"\s*-?\s*\d{4}-\d{2}-\d{2}|\w+ \d{1,2}, \d{4}", "", text).strip()
                    if title:
                        releases.append({
                            "date": date_str,
                            "type": categorize_release(title),
                            "title": title[:100],
                        })
        else:
            for entry in entries[:30]:
                date_elem = entry.find("time") or entry.find(class_=re.compile(r"date"))
                title_elem = entry.find(["h2", "h3", "h4", "a"])

                date_str = ""
                if date_elem:
                    date_str = parse_date(date_elem.get("datetime", "") or date_elem.get_text(strip=True))

                title = title_elem.get_text(strip=True) if title_elem else ""

                if title:
                    releases.append({
                        "date": date_str,
                        "type": categorize_release(title),
                        "title": title[:100],
                    })

        print(f"Scraped {len(releases)} releases from Anthropic changelog")

    except Exception as e:
        print(f"Error scraping Anthropic changelog: {e}")

    # If scraping failed, try GitHub SDK releases as fallback
    if not releases and "github_url" in SOURCES["anthropic"]:
        releases = fetch_github_releases(SOURCES["anthropic"]["github_url"], "Anthropic Python SDK")
        if "github_alt" in SOURCES["anthropic"]:
            alt_releases = fetch_github_releases(SOURCES["anthropic"]["github_alt"], "Anthropic TypeScript SDK")
            existing_dates = {r["date"] for r in releases}
            for r in alt_releases:
                if r["date"] not in existing_dates:
                    releases.append(r)
                    existing_dates.add(r["date"])
            releases.sort(key=lambda x: x.get("date", ""), reverse=True)

    return releases

def fetch_github_releases(url, name):
    """Fetch releases from GitHub API."""
    releases = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        data = response.json()

        for release in data[:30]:
            date_str = parse_date(release.get("published_at", ""))
            title = release.get("name", "") or release.get("tag_name", "")

            if title:
                releases.append({
                    "date": date_str,
                    "type": categorize_release(title),
                    "title": title[:100],
                })

        print(f"Fetched {len(releases)} releases from {name}")

    except Exception as e:
        print(f"Error fetching {name} releases: {e}")

    return releases

def scrape_openai_changelog():
    """Fetch OpenAI releases from GitHub API (SDK releases as proxy for API changes)."""
    releases = []

    # Try OpenAI Python SDK first
    releases = fetch_github_releases(SOURCES["openai"]["url"], "OpenAI Python SDK")

    # Also try Node SDK and merge
    if "alt_url" in SOURCES["openai"]:
        alt_releases = fetch_github_releases(SOURCES["openai"]["alt_url"], "OpenAI Node SDK")
        # Merge and deduplicate by date
        existing_dates = {r["date"] for r in releases}
        for r in alt_releases:
            if r["date"] not in existing_dates:
                releases.append(r)
                existing_dates.add(r["date"])

    # Sort by date descending
    releases.sort(key=lambda x: x.get("date", ""), reverse=True)

    return releases

def scrape_google_changelog():
    """Scrape Google's Gemini API changelog."""
    releases = []

    try:
        response = requests.get(SOURCES["google"]["url"], headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Google typically uses headings with dates
        headings = soup.find_all(["h2", "h3"])

        for heading in headings:
            text = heading.get_text(strip=True)
            date_match = re.search(r"\b(\d{4}-\d{2}-\d{2}|\w+ \d{1,2}, \d{4})\b", text)
            if date_match:
                date_str = parse_date(date_match.group(1))

                # Get the next sibling elements for content
                next_elem = heading.find_next_sibling()
                title = ""
                if next_elem:
                    # Get first list item or paragraph as title
                    li = next_elem.find("li")
                    if li:
                        title = li.get_text(strip=True)[:100]
                    else:
                        title = next_elem.get_text(strip=True)[:100]

                if not title:
                    title = text

                releases.append({
                    "date": date_str,
                    "type": categorize_release(title),
                    "title": title,
                })

        print(f"Scraped {len(releases)} releases from Google")

    except Exception as e:
        print(f"Error scraping Google changelog: {e}")

    return releases

def fetch_meta_github_releases():
    """Fetch Meta's Llama releases from GitHub API."""
    releases = []

    # Try primary repo
    releases = fetch_github_releases(SOURCES["meta"]["url"], "Meta Llama")

    # If no releases, try alternate repo
    if not releases and "alt_url" in SOURCES["meta"]:
        releases = fetch_github_releases(SOURCES["meta"]["alt_url"], "Meta Llama (alt)")

    # If still no releases, try the llama-stack repo
    if not releases:
        releases = fetch_github_releases(
            "https://api.github.com/repos/meta-llama/llama-stack/releases",
            "Meta Llama Stack"
        )

    # Also try llama-recipes for additional activity
    if not releases:
        releases = fetch_github_releases(
            "https://api.github.com/repos/meta-llama/llama-recipes/releases",
            "Meta Llama Recipes"
        )

    return releases

def calculate_activity(releases):
    """Calculate weekly activity counts from releases."""
    activity = []
    now = datetime.utcnow()

    # Count releases per week for last 14 weeks
    for week in range(14):
        week_start = now - timedelta(days=(week + 1) * 7)
        week_end = now - timedelta(days=week * 7)

        count = 0
        for release in releases:
            if release["date"]:
                try:
                    release_date = datetime.strptime(release["date"], "%Y-%m-%d")
                    if week_start <= release_date < week_end:
                        count += 1
                except ValueError:
                    pass

        activity.insert(0, count)

    return activity

from datetime import timedelta

def main():
    """Main function to fetch all changelogs and save pulse data."""
    script_dir = Path(__file__).parent.parent
    output_path = script_dir / "data" / "pulse" / "releases.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Fetching changelog data...")

    companies = {}

    # Anthropic
    anthropic_releases = scrape_anthropic_changelog()
    companies["anthropic"] = {
        "name": "Anthropic",
        "releases": anthropic_releases[:10],
        "activity": calculate_activity(anthropic_releases),
    }

    # OpenAI
    openai_releases = scrape_openai_changelog()
    companies["openai"] = {
        "name": "OpenAI",
        "releases": openai_releases[:10],
        "activity": calculate_activity(openai_releases),
    }

    # Google
    google_releases = scrape_google_changelog()
    companies["google"] = {
        "name": "Google DeepMind",
        "releases": google_releases[:10],
        "activity": calculate_activity(google_releases),
    }

    # Meta
    meta_releases = fetch_meta_github_releases()
    companies["meta"] = {
        "name": "Meta AI",
        "releases": meta_releases[:10],
        "activity": calculate_activity(meta_releases),
    }

    data = {
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "companies": companies,
    }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Saved pulse data to {output_path}")

if __name__ == "__main__":
    main()
