import type { Signals } from "../../types/weather";

interface ShippingDetailProps {
  company: string;
  signals: Signals;
}

export default function ShippingDetail({ company, signals }: ShippingDetailProps) {
  const shipping = signals?.shipping;
  const value = shipping?.value;
  const vsPeers = shipping?.vs_peers;

  const percentage = value != null ? Math.round(value * 100) : null;
  const peerDiff = vsPeers ? Math.round(Math.abs(parseFloat(vsPeers)) * 100) : null;
  const isAbove = vsPeers && parseFloat(vsPeers) > 0;

  return (
    <div className="signal-detail">
      <div className="signal-detail-summary">
        <div className="detail-metric-large">
          <span className="detail-value">{percentage ?? "—"}%</span>
          <span className="detail-label">Shipping Velocity Score</span>
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
          How actively {company} is shipping new features, updates, and improvements. Higher scores indicate more
          frequent and impactful releases.
        </p>
      </div>

      <div className="detail-section">
        <h4>Data Sources</h4>
        <ul className="detail-list">
          <li>Blog post announcements (last 14 days)</li>
          <li>Product changelog updates</li>
          <li>Major feature releases</li>
          <li>API version updates</li>
        </ul>
      </div>

      <div className="detail-section">
        <h4>How It Works</h4>
        <p>
          Release activity is tracked by monitoring official communication channels. Major releases are weighted more
          heavily than minor updates. The score is normalized against the company&apos;s historical shipping cadence.
        </p>
      </div>
    </div>
  );
}
