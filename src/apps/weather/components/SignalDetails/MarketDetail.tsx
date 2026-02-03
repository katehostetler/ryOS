import type { Signals } from "../../types/weather";

const COMPANY_STOCK: Record<string, string | null> = {
  anthropic: null, // Private
  openai: null, // Private
  google: "GOOGL",
  meta: "META",
  xai: null, // Private
};

interface MarketDetailProps {
  company: string;
  signals: Signals;
}

export default function MarketDetail({ company, signals }: MarketDetailProps) {
  const market = signals?.market;
  const value = market?.value;
  const vsPeers = market?.vs_peers;

  const percentage = value != null ? Math.round(value * 100) : null;
  const peerDiff = vsPeers ? Math.round(Math.abs(parseFloat(vsPeers)) * 100) : null;
  const isAbove = vsPeers && parseFloat(vsPeers) > 0;

  const stockSymbol = COMPANY_STOCK[company.toLowerCase()];
  const isPrivate = !stockSymbol;

  return (
    <div className="signal-detail">
      <div className="signal-detail-summary">
        <div className="detail-metric-large">
          <span className="detail-value">{percentage ?? "—"}%</span>
          <span className="detail-label">Market Performance Score</span>
        </div>

        {peerDiff != null && (
          <div className="detail-comparison">
            <span className={`detail-diff ${isAbove ? "positive" : "negative"}`}>
              {isAbove ? "↑" : "↓"} {peerDiff}% {isAbove ? "above" : "below"} peer average
            </span>
          </div>
        )}
      </div>

      {isPrivate ? (
        <div className="detail-section">
          <div className="private-company-notice">
            <span className="notice-icon">🔒</span>
            <div className="notice-text">
              <h4>Private Company</h4>
              <p>
                {company} is a private company. Market score is estimated based on funding rounds, valuation news, and
                industry reports.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="detail-section">
          <h4>Stock Information</h4>
          <p>
            Trading as <strong>{stockSymbol}</strong> on NASDAQ. Score based on 30-day price momentum and relative
            performance.
          </p>
        </div>
      )}

      <div className="detail-section">
        <h4>What This Measures</h4>
        <p>
          {isPrivate
            ? "For private companies, this estimates market perception based on funding activity, valuation changes, and partnership announcements."
            : "Stock price momentum over the past 30 days, normalized to account for overall market conditions."}
        </p>
      </div>

      <div className="detail-section">
        <h4>Data Sources</h4>
        <ul className="detail-list">
          {isPrivate ? (
            <>
              <li>Funding round announcements</li>
              <li>Valuation estimates from industry reports</li>
              <li>Partnership and enterprise deal news</li>
            </>
          ) : (
            <>
              <li>Daily stock price data</li>
              <li>Trading volume analysis</li>
              <li>Sector-relative performance</li>
            </>
          )}
        </ul>
      </div>
    </div>
  );
}
