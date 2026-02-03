import { motion, AnimatePresence } from "framer-motion";
import type { DetailPanelState, DetailType, Signals } from "../../types/weather";
import { SentimentDetail, ShippingDetail, MarketDetail, CompetitiveDetail } from "../SignalDetails";

const DETAIL_COMPONENTS: Record<DetailType, React.FC<{ company: string; signals: Signals }>> = {
  sentiment: SentimentDetail,
  shipping: ShippingDetail,
  market: MarketDetail,
  competitive: CompetitiveDetail,
};

const DETAIL_TITLES: Record<DetailType, string> = {
  sentiment: "Sentiment Analysis",
  shipping: "Shipping Activity",
  market: "Market Performance",
  competitive: "Competitive Ranking",
};

interface DetailPanelProps {
  detailPanel: DetailPanelState | null;
  onClose: () => void;
}

export default function DetailPanel({ detailPanel, onClose }: DetailPanelProps) {
  const DetailComponent = detailPanel ? DETAIL_COMPONENTS[detailPanel.type] : null;
  const title = detailPanel ? DETAIL_TITLES[detailPanel.type] : "";

  return (
    <AnimatePresence>
      {detailPanel && (
        <>
          {/* Backdrop */}
          <motion.div
            className="detail-panel-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            className="detail-panel"
            initial={{ x: "100%", opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: "100%", opacity: 0 }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
          >
            {/* Header */}
            <div className="detail-panel-header">
              <h3>{title}</h3>
              <button className="detail-panel-close" onClick={onClose}>
                ×
              </button>
            </div>

            {/* Content */}
            <div className="detail-panel-content">
              {DetailComponent && <DetailComponent company={detailPanel.company} signals={detailPanel.signals} />}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
