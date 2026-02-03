import type { Signals } from "../../types/weather";

interface SentimentDetailProps {
  company: string;
  signals: Signals;
}

export default function SentimentDetail({ company, signals }: SentimentDetailProps) {
  const sentiment = signals?.sentiment;
  const value = sentiment?.value;
  const vsPeers = sentiment?.vs_peers;

  const percentage = value != null ? Math.round(value * 100) : null;
  const peerDiff = vsPeers ? Math.round(Math.abs(parseFloat(vsPeers)) * 100) : null;
  const isAbove = vsPeers && parseFloat(vsPeers) > 0;

  return (
    <div className="signal-detail">
      <div className="signal-detail-summary">
        <div className="detail-metric-large">
          <span className="detail-value">{percentage ?? "—"}%</span>
          <span className="detail-label">Overall Sentiment Score</span>
        </div>

        {peerDiff != null && (
          <div className="detail-comparison">
            <span className={`detail-diff ${isAbove ? "positive" : "negative"}`}>
              {isAbove ? "↑" : "↓"} {peerDiff}% {isAbove ? "above" : "below"} peer average
            </span>
          </div>
        )}
      </div>

      <div className="detail-section">
        <h4>What This Measures</h4>
        <p>
          Sentiment analysis of recent blog posts and HackerNews discussions mentioning {company}. The score ranges
          from 0% (very negative) to 100% (very positive), with 50% being neutral.
        </p>
      </div>

      <div className="detail-section">
        <h4>Data Sources</h4>
        <ul className="detail-list">
          <li>Company blog posts from the last 7 days</li>
          <li>HackerNews front page stories and comments</li>
          <li>Technical discussion sentiment analysis</li>
        </ul>
      </div>

      <div className="detail-section">
        <h4>How It Works</h4>
        <p>
          Blog posts are analyzed for positive/negative language. HackerNews discussions are weighted by comment score
          and engagement. The final score is a weighted average of both sources, normalized to account for typical
          discussion patterns.
        </p>
      </div>
    </div>
  );
}
