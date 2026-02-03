import { motion } from "framer-motion";
import { TabGroup } from "../Shared";
import CompanyCard from "./CompanyCard";
import type { CompanyForecast, MoodData, TimeframeType } from "../../types/weather";
import { COMPANIES } from "../../types/weather";

const TIMEFRAME_TABS = [
  { id: "7d", label: "7 Day" },
  { id: "14d", label: "14 Day" },
  { id: "30d", label: "30 Day" },
];

interface OverviewViewProps {
  forecast: Record<string, CompanyForecast> | undefined;
  moods: Record<string, MoodData>;
  lastUpdated: string | undefined;
  timeframe: TimeframeType;
  onTimeframeChange: (timeframe: TimeframeType) => void;
  onCompanyClick: (companyId: string) => void;
  onRefresh: () => void;
}

export default function OverviewView({
  forecast,
  moods,
  lastUpdated,
  timeframe,
  onTimeframeChange,
  onCompanyClick,
  onRefresh,
}: OverviewViewProps) {
  return (
    <div className="overview-view">
      {/* Header */}
      <div className="overview-header">
        <div className="overview-title">
          <h1>AI Weather Forecast</h1>
          <p className="overview-subtitle">Tracking the climate of artificial intelligence</p>
        </div>

        <div className="overview-controls">
          <TabGroup
            tabs={TIMEFRAME_TABS}
            activeTab={timeframe}
            onTabChange={(id) => onTimeframeChange(id as TimeframeType)}
          />
          <button className="refresh-button" onClick={onRefresh}>
            ↻ Refresh
          </button>
        </div>
      </div>

      {/* Company Cards Grid */}
      <motion.div
        className="company-grid"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {COMPANIES.map((company, index) => (
          <motion.div
            key={company.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <CompanyCard
              company={company}
              forecast={forecast?.[company.id]}
              mood={moods[company.id]}
              onClick={() => onCompanyClick(company.id)}
            />
          </motion.div>
        ))}
      </motion.div>

      {/* Footer */}
      <div className="overview-footer">
        {lastUpdated && (
          <span className="last-updated">
            Last updated: {new Date(lastUpdated).toLocaleString()}
          </span>
        )}
      </div>
    </div>
  );
}
