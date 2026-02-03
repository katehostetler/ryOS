#!/usr/bin/env python3
"""
Fetch blog/news feeds for AI companies.
Uses RSS where available, web scraping where not.
Outputs to data/mood/{company}.json
"""

import json
import re
from datetime import datetime
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup

# RSS feeds and scraping targets
SOURCES = {
    "openai": {
        "type": "rss",
        "url": "https://openai.com/blog/rss.xml",
        "name": "OpenAI",
    },
    "google": {
        "type": "rss",
        "url": "https://blog.google/technology/ai/rss/",
        "name": "Google DeepMind",
    },
    "meta": {
        "type": "rss",
        "url": "https://about.fb.com/news/feed/",
        "name": "Meta AI",
        "filter_keywords": ["ai", "llama", "artificial intelligence", "machine learning", "meta ai"],
    },
    "anthropic": {
        "type": "scrape",
        "url": "https://www.anthropic.com/news",
        "name": "Anthropic",
    },
}

def fetch_rss_feed(source):
    """Fetch posts from an RSS feed."""
    posts = []

    try:
        feed = feedparser.parse(source["url"])

        for entry in feed.entries[:20]:  # Get up to 20 entries
            title = entry.get("title", "")

            # Apply keyword filter if specified
            if "filter_keywords" in source:
                title_lower = title.lower()
                summary_lower = entry.get("summary", "").lower()
                if not any(kw in title_lower or kw in summary_lower for kw in source["filter_keywords"]):
                    continue

            # Parse date
            date_str = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                date_str = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                date_str = datetime(*entry.updated_parsed[:6]).strftime("%Y-%m-%d")

            posts.append({
                "title": title,
                "date": date_str,
                "url": entry.get("link", ""),
                "summary": entry.get("summary", "")[:500],  # Truncate summary
            })

        print(f"Fetched {len(posts)} posts from {source['name']} RSS")

    except Exception as e:
        print(f"Error fetching RSS from {source['url']}: {e}")

    return posts

def scrape_anthropic_news():
    """Scrape news from Anthropic's website with proper date extraction.

    Anthropic uses Next.js - we extract data from the rendered DOM
    which has the complete article information.
    """
    posts = []
    seen_urls = set()
    url = "https://www.anthropic.com/news"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Primary: DOM-based scraping (most reliable for complete data)
        posts = scrape_anthropic_dom_fallback(soup, seen_urls)

        # Fallback: Try JSON extraction if DOM scraping fails
        if not posts:
            posts_found = extract_posts_from_nextjs_data(html)
            if posts_found:
                for post in posts_found:
                    if post["url"] not in seen_urls:
                        seen_urls.add(post["url"])
                        posts.append(post)

    except Exception as e:
        print(f"Error scraping Anthropic news page: {e}")

    # Also scrape special landing pages (not under /news/)
    special_pages = scrape_anthropic_special_pages(headers, seen_urls)
    posts = special_pages + posts  # Put special pages first (usually more recent)

    print(f"Scraped {len(posts)} posts from Anthropic")
    return posts


def scrape_anthropic_special_pages(headers, seen_urls):
    """Scrape special landing pages that aren't under /news/."""
    special_posts = []

    # Known special pages with metadata
    # These are major announcements with dedicated landing pages
    special_pages = [
        {
            "url": "https://www.anthropic.com/mars",
            "fallback_title": "Claude on Mars",
            "fallback_date": "2026-01-30",  # Announced Jan 30, 2026
        },
        # /claude is a product page, not news - skip it
    ]

    for page_info in special_pages:
        page_url = page_info["url"]
        if page_url in seen_urls:
            continue

        try:
            response = requests.get(page_url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            # Try to extract title - prefer og:title, then h1, then title tag
            title = None
            og_title = soup.find("meta", {"property": "og:title"})
            if og_title:
                title = og_title.get("content", "").strip()

            if not title:
                h1 = soup.find("h1")
                if h1:
                    title = h1.get_text(strip=True)

            if not title:
                title_tag = soup.find("title")
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    title = title.replace(" | Anthropic", "").replace(" - Anthropic", "").strip()

            # Use fallback title if extraction failed
            if not title or len(title) < 5:
                title = page_info.get("fallback_title", "")

            if not title:
                continue

            # Try to find date - use fallback if not found
            date_str = page_info.get("fallback_date", "")

            # Try to get summary/description
            summary = ""
            meta_desc = soup.find("meta", {"property": "og:description"}) or soup.find("meta", {"name": "description"})
            if meta_desc:
                summary = meta_desc.get("content", "")[:500]

            seen_urls.add(page_url)
            special_posts.append({
                "title": title,
                "date": date_str,
                "url": page_url,
                "summary": summary,
            })

        except Exception as e:
            print(f"Error scraping special page {page_url}: {e}")

    return special_posts


def extract_posts_from_nextjs_data(html):
    """Extract post data from Next.js embedded JSON."""
    posts = []
    seen_slugs = set()

    # Try to find the __NEXT_DATA__ script tag first (most reliable)
    next_data_pattern = r'<script id="__NEXT_DATA__"[^>]*>([^<]+)</script>'
    match = re.search(next_data_pattern, html)
    if match:
        try:
            data = json.loads(match.group(1))
            posts = extract_from_next_data_json(data)
            if posts:
                return posts
        except (json.JSONDecodeError, KeyError):
            pass

    # Fallback: Extract individual fields and correlate by position/proximity
    # Find all title-slug-date triplets in the embedded JSON

    # Look for title followed by slug pattern within reasonable distance
    # The title field appears before slug in the JSON structure
    pattern = r'"title"\s*:\s*"([^"]+)"[^}]*?"slug"\s*:\s*\{\s*"current"\s*:\s*"([^"]+)"'
    title_slug_matches = re.findall(pattern, html, re.DOTALL)

    # Also extract publishedOn dates
    date_pattern = r'"publishedOn"\s*:\s*"([^"]+)"'
    dates = re.findall(date_pattern, html)

    # Match titles with slugs and try to find corresponding dates
    for i, (title, slug) in enumerate(title_slug_matches):
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        # Skip generic/navigation titles
        if len(title) < 10 or title.lower() in ['news', 'research', 'announcements']:
            continue

        # Try to get date - use index if available
        formatted_date = ""
        if i < len(dates):
            try:
                parsed_date = datetime.fromisoformat(dates[i].replace('Z', '+00:00'))
                formatted_date = parsed_date.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                pass

        post_url = f"https://www.anthropic.com/news/{slug}"

        posts.append({
            "title": title,
            "date": formatted_date,
            "url": post_url,
            "summary": "",
        })

    return posts


def extract_from_next_data_json(data):
    """Extract posts from parsed __NEXT_DATA__ JSON."""
    posts = []

    def find_posts(obj, path=""):
        """Recursively find post objects in the JSON structure."""
        if isinstance(obj, dict):
            # Check if this looks like a post object
            if "publishedOn" in obj and "title" in obj:
                try:
                    date_str = obj.get("publishedOn", "")
                    if date_str:
                        parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        formatted_date = parsed_date.strftime("%Y-%m-%d")
                    else:
                        formatted_date = ""

                    title = obj.get("title", "")
                    slug = obj.get("slug", {})
                    if isinstance(slug, dict):
                        slug = slug.get("current", "")

                    if title and slug:
                        posts.append({
                            "title": title,
                            "date": formatted_date,
                            "url": f"https://www.anthropic.com/news/{slug}",
                            "summary": obj.get("excerpt", "")[:500] if obj.get("excerpt") else "",
                        })
                except (ValueError, TypeError, AttributeError):
                    pass

            # Continue searching nested objects
            for key, value in obj.items():
                find_posts(value, f"{path}.{key}")

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                find_posts(item, f"{path}[{i}]")

    find_posts(data)
    return posts


def scrape_anthropic_dom_fallback(soup, seen_urls):
    """DOM-based scraping for Anthropic news articles.

    The link text contains: Category + Date + Title + Summary (concatenated)
    We need to extract the title and date from this mixed content.
    """
    posts = []

    # Common category prefixes in Anthropic's news
    categories = ['Announcements', 'Announcement', 'Research', 'Product', 'Policy',
                  'Case Study', 'CaseStudy', 'News', 'Company']

    # Find all news article links
    for link in soup.select('a[href*="/news/"]'):
        href = link.get('href', '')

        # Skip non-article links
        if not href or href == '/news' or href == '/news/':
            continue
        if 'mailto:' in href:
            continue
        # Skip external links
        if href.startswith('http') and 'anthropic.com' not in href:
            continue

        # Build full URL
        if href.startswith('/'):
            full_url = f"https://www.anthropic.com{href}"
        else:
            full_url = href

        # Skip if already seen
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        # Get full text content
        raw_text = link.get_text(strip=True)

        if not raw_text or len(raw_text) < 10:
            continue

        # Parse the concatenated text to extract date and title
        title, date_str = parse_anthropic_article_text(raw_text, categories)

        if not title or len(title) < 5:
            continue

        posts.append({
            "title": title,
            "date": date_str,
            "url": full_url,
            "summary": "",
        })

        if len(posts) >= 30:
            break

    return posts


def parse_anthropic_article_text(text, categories):
    """Parse article text that may contain: Category + Date + Title + Summary.

    Examples:
    - "AnnouncementsSep 29, 2025Introducing Claude Sonnet 4.5Claude Sonnet 4.5 sets..."
    - "Jan 28, 2026AnnouncementsServiceNow chooses Claude..."
    - "ProductOct 15, 2025Introducing Claude Haiku 4.5..."
    """
    # Date patterns
    date_pattern = r'([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})'

    # Try to find date in the text
    date_match = re.search(date_pattern, text)
    date_str = ""
    if date_match:
        try:
            parsed = datetime.strptime(date_match.group(1), "%b %d, %Y")
            date_str = parsed.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Remove date from text
    text_no_date = re.sub(date_pattern, '|||', text)

    # Remove category prefixes
    for cat in categories:
        text_no_date = text_no_date.replace(cat, '|||')

    # Split by delimiter and find the title (usually the first meaningful segment after date/category)
    parts = [p.strip() for p in text_no_date.split('|||') if p.strip()]

    if not parts:
        # Fallback: just remove date and take what's left
        title = re.sub(date_pattern, '', text).strip()
        for cat in categories:
            title = title.replace(cat, '').strip()
        return clean_title_from_summary(title), date_str

    # Find the title - first substantial part
    title = ""
    for part in parts:
        if len(part) > 10 and part[0].isupper():
            title = clean_title_from_summary(part)
            break

    if not title and parts:
        title = clean_title_from_summary(parts[0])

    return title, date_str


def clean_title_from_summary(text):
    """Separate title from appended summary text.

    Titles often have summaries appended like:
    "Introducing Claude Opus 4.5The best model in the world..."
    We want just "Introducing Claude Opus 4.5"
    """
    if not text or len(text) < 20:
        return text

    # Pattern 1: Title ends with version number, summary starts with "The/A/An"
    # e.g., "...4.5The best..." -> "...4.5"
    match = re.search(r'^(.+?\d+\.?\d*)(The |A |An |It |This |We |Our )', text)
    if match:
        return match.group(1).strip()

    # Pattern 2: Title ends with word, then uppercase word without space starts summary
    # e.g., "...productivityServiceNow expanded..." -> look for CamelCase boundary
    # Find where a lowercase letter is immediately followed by uppercase (title|Summary boundary)
    match = re.search(r'^(.+?[a-z])([A-Z][a-z])', text)
    if match and len(match.group(1)) > 15:
        potential_title = match.group(1)
        # Verify this looks like a complete title (not mid-word)
        # Should end with a complete word
        if re.search(r'\b\w+$', potential_title):
            return potential_title.strip()

    # Pattern 3: Title contains repeated key phrase (title repeated in summary)
    # e.g., "Introducing Claude Haiku 4.5Claude Haiku 4.5 matches..."
    words = text.split()
    if len(words) > 6:
        # Look for 2-3 word phrase that repeats
        for phrase_len in [3, 2]:
            for i in range(len(words) - phrase_len * 2):
                phrase = ' '.join(words[i:i+phrase_len])
                rest = ' '.join(words[i+phrase_len:])
                if phrase.lower() in rest.lower():
                    # Found repeat - title is up to first occurrence
                    return ' '.join(words[:i+phrase_len]).strip()

    # Pattern 4: Very long text - likely includes summary, truncate reasonably
    if len(text) > 80:
        # Try to end at a natural boundary
        # Look for end of a phrase/clause
        truncated = text[:80]
        # Find last complete word
        last_space = truncated.rfind(' ')
        if last_space > 40:
            return truncated[:last_space].strip()
        return truncated.strip()

    return text

def scrape_meta_ai_blog():
    """Scrape AI-specific posts from Meta's AI blog."""
    posts = []
    url = "https://ai.meta.com/blog/"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AI-Weather-Report/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Find blog post links
        articles = soup.find_all("a", href=re.compile(r"/blog/"))

        seen_urls = set()
        for article in articles:
            link_url = article.get("href", "")
            if not link_url.startswith("http"):
                link_url = f"https://ai.meta.com{link_url}"

            if link_url in seen_urls:
                continue
            seen_urls.add(link_url)

            title_elem = article.find(["h2", "h3", "h4"]) or article
            title = title_elem.get_text(strip=True) if title_elem else ""

            if not title or len(title) < 5:
                continue

            posts.append({
                "title": title,
                "date": "",
                "url": link_url,
                "summary": "",
            })

            if len(posts) >= 30:
                break

        print(f"Scraped {len(posts)} posts from Meta AI blog")

    except Exception as e:
        print(f"Error scraping Meta AI blog: {e}")

    return posts

def load_existing_data(filepath):
    """Load existing mood data file if it exists."""
    if filepath.exists():
        try:
            with open(filepath) as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_mood_data(company_id, name, posts, output_dir):
    """Save mood data for a company, preserving history."""
    filepath = output_dir / f"{company_id}.json"
    existing = load_existing_data(filepath)

    # Preserve existing history if available
    history = existing.get("history", []) if existing else []
    sentiment = existing.get("sentiment", {"score": 0.0, "label": "cautious"}) if existing else {"score": 0.0, "label": "cautious"}

    data = {
        "company": name,
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "sentiment": sentiment,
        "posts": posts[:20],  # Keep most recent 20
        "history": history,
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Saved mood data to {filepath}")

def main():
    """Main function to fetch all feeds and save mood data."""
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / "public" / "data" / "mood"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching blog/news feeds...")

    for company_id, source in SOURCES.items():
        if source["type"] == "rss":
            posts = fetch_rss_feed(source)
        elif company_id == "anthropic":
            posts = scrape_anthropic_news()

        save_mood_data(company_id, source["name"], posts, output_dir)

    # Also scrape Meta AI blog for additional AI-specific content
    meta_ai_posts = scrape_meta_ai_blog()
    if meta_ai_posts:
        # Merge with existing Meta posts
        meta_path = output_dir / "meta.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta_data = json.load(f)
            # Add unique posts from AI blog
            existing_urls = {p["url"] for p in meta_data.get("posts", [])}
            for post in meta_ai_posts:
                if post["url"] not in existing_urls:
                    meta_data["posts"].insert(0, post)
            meta_data["posts"] = meta_data["posts"][:10]
            with open(meta_path, 'w') as f:
                json.dump(meta_data, f, indent=2)

    print("Feed fetching complete!")

if __name__ == "__main__":
    main()
