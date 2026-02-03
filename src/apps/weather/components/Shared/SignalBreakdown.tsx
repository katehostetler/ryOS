import { motion } from "framer-motion";
import type { Signals, DetailType, SignalConfig } from "../../types/weather";
import { SIGNAL_CONFIG } from "../../types/weather";

// Convert vs_peers value to readable format
function formatVsPeers(vsPeers: string | null): { text: string; isPositive: boolean; isNeutral: boolean } | null {
  if (!vsPeers) return null;

  const value = parseFloat(vsPeers);
  const absValue = Math.abs(value);
  const percentage = Math.round(absValue * 100);

  if (percentage === 0) {
    return { text: "At average", isPositive: true, isNeutral: true };
  }

  if (value > 0) {
    return { text: `${percentage}% above avg`, isPositive: true, isNeutral: false };
  } else {
    return { text: `${percentage}% below avg`, isPositive: false, isNeutral: false };
  }
}

// Calculate rank from vs_peers (approximation)
function calculateRank(vsPeers: string | null): { rank: number; total: number } | null {
  if (!vsPeers) return null;
  const value = parseFloat(vsPeers);

  // Approximate ranking: top performer > +0.1, bottom performer < -0.1
  if (value > 0.1) return { rank: 1, total: 5 };
  if (value > 0) return { rank: 2, total: 5 };
  if (value > -0.05) return { rank: 3, total: 5 };
  if (value > -0.1) return { rank: 4, total: 5 };
  return { rank: 5, total: 5 };
}

interface SignalBarProps {
  value: number | null;
  isStormy: boolean;
}

function SignalBar({ value, isStormy }: SignalBarProps) {
  const percentage = value != null ? Math.round(value * 100) : 0;
  const barColor = value != null && value >= 0.6 ? "#22C55E" : value != null && value >= 0.4 ? "#EAB308" : "#EF4444";

  return (
    <div className="signal-bar-container-improved">
      <div className="signal-bar-background-improved">
        <motion.div
          className="signal-bar-fill-improved"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          style={{ backgroundColor: barColor }}
        />
      </div>
      <span className={`signal-bar-value-improved ${isStormy ? "stormy" : ""}`}>
        {value != null ? `${percentage}%` : "N/A"}
      </span>
    </div>
  );
}

interface VsPeersBadgeProps {
  vsPeers: string | null;
  isStormy: boolean;
}

function VsPeersBadgeImproved({ vsPeers, isStormy }: VsPeersBadgeProps) {
  const formatted = formatVsPeers(vsPeers);
  if (!formatted) return null;

  const rankInfo = calculateRank(vsPeers);

  return (
    <div className="vs-peers-improved">
      <span
        className={`vs-peers-text ${formatted.isPositive ? "positive" : "negative"} ${formatted.isNeutral ? "neutral" : ""} ${isStormy ? "stormy" : ""}`}
      >
        {formatted.isPositive && !formatted.isNeutral && "▲ "}
        {!formatted.isPositive && "▼ "}
        {formatted.text}
      </span>
      {rankInfo && (
        <span className={`rank-badge ${isStormy ? "stormy" : ""}`}>
          #{rankInfo.rank} of {rankInfo.total}
        </span>
      )}
    </div>
  );
}

interface SignalItemProps {
  signal: { value: number | null; vs_peers: string | null };
  config: SignalConfig;
  isStormy: boolean;
  onDetailClick: (detailType: DetailType) => void;
}

function SignalItem({ signal, config, isStormy, onDetailClick }: SignalItemProps) {
  const iconMap: Record<string, string> = {
    "message-circle": "💭",
    rocket: "🚀",
    "trending-up": "📈",
    trophy: "🏆",
  };

  return (
    <motion.div
      className={`signal-item-improved ${isStormy ? "stormy" : ""}`}
      whileHover={{ backgroundColor: isStormy ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.04)" }}
      onClick={() => onDetailClick(config.detailType)}
      style={{ cursor: "pointer" }}
    >
      {/* Header row */}
      <div className="signal-header-improved">
        <span className="signal-icon-improved">{iconMap[config.icon] || "📊"}</span>
        <span className={`signal-label-improved ${isStormy ? "stormy" : ""}`}>{config.label}</span>
        <VsPeersBadgeImproved vsPeers={signal.vs_peers} isStormy={isStormy} />
      </div>

      {/* Description */}
      <div className={`signal-description ${isStormy ? "stormy" : ""}`}>{config.description}</div>

      {/* Progress bar */}
      <SignalBar value={signal.value} isStormy={isStormy} />

      {/* Footer with time window and details link */}
      <div className="signal-footer">
        <span className={`signal-time-window ${isStormy ? "stormy" : ""}`}>{config.timeWindow}</span>
        <span className={`signal-details-link ${isStormy ? "stormy" : ""}`}>Details →</span>
      </div>
    </motion.div>
  );
}

interface SignalBreakdownProps {
  signals: Signals | null;
  isStormy?: boolean;
  company: string;
  onDetailClick: (detailType: DetailType) => void;
}

export default function SignalBreakdown({
  signals,
  isStormy = false,
  company: _company,
  onDetailClick,
}: SignalBreakdownProps) {
  if (!signals) return null;

  return (
    <div className={`signal-breakdown-improved ${isStormy ? "stormy" : ""}`}>
      <div className="signal-list-improved">
        {(Object.entries(SIGNAL_CONFIG) as [keyof Signals, SignalConfig][]).map(([key, config]) => {
          const signal = signals[key];
          if (!signal) return null;

          return (
            <SignalItem
              key={key}
              signal={signal}
              config={config}
              isStormy={isStormy}
              onDetailClick={onDetailClick}
            />
          );
        })}
      </div>
    </div>
  );
}
