#!/usr/bin/env python3
"""
Calculate composite weather scores for AI companies.
Combines signals from mood (sentiment), pulse (shipping), pressure (market), and buzz (HN).
Outputs to data/forecast.json
"""

import json
from datetime import datetime
from pathlib import Path

# Weather thresholds
WEATHER_THRESHOLDS = {
    "sunny": 0.6,      # Score > 0.6
    "partly_cloudy": 0.3,  # Score > 0.3
    "cloudy": 0.0,     # Score > 0
    "rainy": -0.3,     # Score > -0.3
    "stormy": -1.0,    # Everything else
}

# Weather display info
WEATHER_INFO = {
    "sunny": {"icon": "sunny", "emoji": "sunny", "label": "Sunny", "description": "Bright outlook with strong signals"},
    "partly_cloudy": {"icon": "cloudy", "emoji": "partly_cloudy", "label": "Partly Cloudy", "description": "Mixed signals, some uncertainty"},
    "cloudy": {"icon": "cloudy", "emoji": "cloudy", "label": "Cloudy", "description": "Below average performance"},
    "rainy": {"icon": "stormy", "emoji": "rainy", "label": "Rainy", "description": "Concerning trends emerging"},
    "stormy": {"icon": "stormy", "emoji": "stormy", "label": "Stormy", "description": "Turbulent times ahead"},
    "foggy": {"icon": "foggy", "emoji": "foggy", "label": "Foggy", "description": "Insufficient data available"},
}

# Signal weights
WEIGHTS = {
    "sentiment": 0.25,
    "shipping": 0.25,
    "market": 0.25,
    "competitive": 0.25,
}

# Company to stock ticker mapping
COMPANY_STOCK_MAP = {
    "anthropic": None,  # Private
    "openai": "MSFT",   # Proxy via Microsoft
    "google": "GOOGL",
    "meta": "META",
}


def load_json(path):
    """Load a JSON file, return None if not found."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load {path}: {e}")
        return None


def normalize_score(value, min_val, max_val):
    """Normalize a value to 0-1 range."""
    if max_val == min_val:
        return 0.5
    return max(0, min(1, (value - min_val) / (max_val - min_val)))


def calculate_sentiment_score(mood_data, buzz_data, company_id):
    """
    Calculate sentiment score (0-1) from mood and HN buzz data.
    """
    scores = []

    # Blog sentiment from mood data
    if mood_data and "sentiment" in mood_data:
        # Sentiment score is typically -1 to 1, normalize to 0-1
        raw_score = mood_data["sentiment"].get("score", 0)
        scores.append((raw_score + 1) / 2)

    # HN sentiment from buzz data
    if buzz_data and "companies" in buzz_data:
        company_buzz = buzz_data["companies"].get(company_id, {})
        hn_sentiment = company_buzz.get("sentiment", 0)
        # HN sentiment is -1 to 1, normalize to 0-1
        scores.append((hn_sentiment + 1) / 2)

    return sum(scores) / len(scores) if scores else None


def calculate_shipping_score(pulse_data, company_id):
    """
    Calculate shipping/release velocity score (0-1).
    Based on recent releases and activity levels.
    """
    if not pulse_data or "companies" not in pulse_data:
        return None

    company_pulse = pulse_data["companies"].get(company_id, {})
    activity = company_pulse.get("activity", [])
    releases = company_pulse.get("releases", [])

    if not activity:
        return None

    # Recent activity (last 7 entries = last week)
    recent_activity = activity[:7] if len(activity) >= 7 else activity
    avg_recent = sum(recent_activity) / len(recent_activity) if recent_activity else 0

    # Normalize: 0 releases = 0, 5+ releases/week = 1
    return min(1.0, avg_recent / 3.0)


def calculate_market_score(stocks_data, company_id):
    """
    Calculate market momentum score (0-1).
    Based on stock performance over recent period.
    """
    if not stocks_data or "stocks" not in stocks_data:
        return None

    ticker = COMPANY_STOCK_MAP.get(company_id)
    if not ticker:
        return None  # Private company

    stock = next((s for s in stocks_data["stocks"] if s["ticker"] == ticker), None)
    if not stock:
        return None

    history = stock.get("history", [])
    if len(history) < 10:
        return None

    # Calculate momentum: recent price vs 30-day average
    recent_price = history[-1] if history else 0
    avg_30d = sum(history[-30:]) / min(len(history), 30) if history else 0

    if avg_30d == 0:
        return 0.5

    # Momentum ratio: 0.9 = -10%, 1.1 = +10%
    momentum = recent_price / avg_30d

    # Normalize: 0.8 (-20%) = 0, 1.0 (0%) = 0.5, 1.2 (+20%) = 1.0
    return max(0, min(1, (momentum - 0.8) / 0.4))


def calculate_competitive_score(buzz_data, pulse_data, company_id, all_companies):
    """
    Calculate competitive position score (0-1).
    Based on relative HN buzz and shipping velocity vs peers.
    """
    if not buzz_data or not pulse_data:
        return None

    scores = []

    # HN buzz relative to peers
    company_buzz = buzz_data.get("companies", {}).get(company_id, {})
    company_points = company_buzz.get("total_points", 0)

    all_points = [
        buzz_data.get("companies", {}).get(c, {}).get("total_points", 0)
        for c in all_companies
    ]
    max_points = max(all_points) if all_points else 1
    if max_points > 0:
        scores.append(company_points / max_points)

    # Shipping velocity relative to peers
    company_pulse = pulse_data.get("companies", {}).get(company_id, {})
    company_activity = sum(company_pulse.get("activity", [])[:7])

    all_activity = [
        sum(pulse_data.get("companies", {}).get(c, {}).get("activity", [])[:7])
        for c in all_companies
    ]
    max_activity = max(all_activity) if all_activity else 1
    if max_activity > 0:
        scores.append(company_activity / max_activity)

    return sum(scores) / len(scores) if scores else None


def calculate_vs_peers(value, all_values):
    """Calculate difference vs peer average."""
    if value is None or not all_values:
        return None
    valid_values = [v for v in all_values if v is not None]
    if not valid_values:
        return None
    avg = sum(valid_values) / len(valid_values)
    diff = value - avg
    return f"+{diff:.2f}" if diff >= 0 else f"{diff:.2f}"


def determine_weather(score):
    """Determine weather state from composite score."""
    if score is None:
        return "foggy"
    # Convert 0-1 score to -1 to 1 range for thresholds
    adjusted_score = (score * 2) - 1

    if adjusted_score > WEATHER_THRESHOLDS["sunny"]:
        return "sunny"
    elif adjusted_score > WEATHER_THRESHOLDS["partly_cloudy"]:
        return "partly_cloudy"
    elif adjusted_score > WEATHER_THRESHOLDS["cloudy"]:
        return "cloudy"
    elif adjusted_score > WEATHER_THRESHOLDS["rainy"]:
        return "rainy"
    else:
        return "stormy"


def generate_summary(signals, weather, company_id):
    """Generate a human-readable summary of the company's weather."""
    strengths = []
    weaknesses = []

    for signal_name, signal_data in signals.items():
        vs_peers = signal_data.get("vs_peers", "")
        if vs_peers and vs_peers.startswith("+") and float(vs_peers[1:]) > 0.1:
            strengths.append(signal_name)
        elif vs_peers and vs_peers.startswith("-") and float(vs_peers[1:]) < -0.1:
            weaknesses.append(signal_name)

    if strengths and not weaknesses:
        return f"Outperforming on {', '.join(strengths)}"
    elif weaknesses and not strengths:
        return f"Challenges in {', '.join(weaknesses)}"
    elif strengths and weaknesses:
        return f"Strong {', '.join(strengths)}; watching {', '.join(weaknesses)}"
    else:
        return WEATHER_INFO.get(weather, {}).get("description", "Performance tracking")


def main():
    """Calculate weather for all companies and save forecast."""
    script_dir = Path(__file__).parent.parent
    data_dir = script_dir / "public" / "data"

    # Load all data sources
    mood_data = {}
    for company in ["anthropic", "openai", "google", "meta"]:
        mood_data[company] = load_json(data_dir / "mood" / f"{company}.json")

    pulse_data = load_json(data_dir / "pulse" / "releases.json")
    stocks_data = load_json(data_dir / "pressure" / "stocks.json")
    buzz_data = load_json(data_dir / "buzz" / "hackernews.json")

    all_companies = ["anthropic", "openai", "google", "meta"]

    print("Calculating weather forecasts...")

    # First pass: calculate all individual scores
    all_scores = {company: {} for company in all_companies}

    for company in all_companies:
        all_scores[company]["sentiment"] = calculate_sentiment_score(
            mood_data.get(company), buzz_data, company
        )
        all_scores[company]["shipping"] = calculate_shipping_score(pulse_data, company)
        all_scores[company]["market"] = calculate_market_score(stocks_data, company)
        all_scores[company]["competitive"] = calculate_competitive_score(
            buzz_data, pulse_data, company, all_companies
        )

    # Second pass: calculate vs_peers and final weather
    forecast = {}

    for company in all_companies:
        signals = {}

        for signal_name in ["sentiment", "shipping", "market", "competitive"]:
            value = all_scores[company][signal_name]
            all_values = [all_scores[c][signal_name] for c in all_companies]
            vs_peers = calculate_vs_peers(value, all_values)

            signals[signal_name] = {
                "value": round(value, 2) if value is not None else None,
                "vs_peers": vs_peers,
            }

        # Calculate composite score
        weighted_sum = 0
        total_weight = 0
        for signal_name, weight in WEIGHTS.items():
            value = all_scores[company][signal_name]
            if value is not None:
                weighted_sum += value * weight
                total_weight += weight

        composite_score = weighted_sum / total_weight if total_weight > 0 else None
        weather = determine_weather(composite_score)

        forecast[company] = {
            "weather": weather,
            "weather_info": WEATHER_INFO.get(weather, WEATHER_INFO["foggy"]),
            "score": round(composite_score, 2) if composite_score is not None else None,
            "signals": signals,
            "summary": generate_summary(signals, weather, company),
        }

        score_str = f"{composite_score:.2f}" if composite_score is not None else "N/A"
        print(f"  {company}: {weather} (score: {score_str})")

    result = {
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "forecast": forecast,
    }

    # Save to both locations
    output_paths = [
        data_dir / "forecast.json",
        script_dir / "data" / "forecast.json",
    ]

    for output_path in output_paths:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Saved forecast to {output_path}")

    print("Weather calculation complete!")


if __name__ == "__main__":
    main()
