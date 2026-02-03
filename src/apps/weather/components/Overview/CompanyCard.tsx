import { motion } from "framer-motion";
import { WeatherIcon, Sparkline } from "../Shared";
import type { Company, CompanyForecast, MoodData, WeatherType } from "../../types/weather";

interface CompanyCardProps {
  company: Company;
  forecast?: CompanyForecast;
  mood?: MoodData;
  onClick: () => void;
}

export default function CompanyCard({ company, forecast, mood, onClick }: CompanyCardProps) {
  const weather = (forecast?.weather || "foggy") as WeatherType;
  const score = forecast?.score ? Math.round(forecast.score * 100) : null;

  // Get signal summaries
  const sentimentValue = forecast?.signals?.sentiment?.value;
  const shippingValue = forecast?.signals?.shipping?.value;
  const marketValue = forecast?.signals?.market?.value;

  const formatSignal = (value: number | null | undefined, label: string) => {
    if (value == null) return `${label}: No data`;
    const pct = Math.round(value * 100);
    return `${label}: ${pct}%`;
  };

  return (
    <motion.div
      className="company-card"
      onClick={onClick}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="company-card-header">
        <div className="company-card-icon">
          <WeatherIcon weather={weather} size="medium" animated />
        </div>
        <div className="company-card-title">
          <h3>{company.name}</h3>
          <span className="company-card-weather-label">
            {forecast?.weather_info?.label || "Unknown"}
          </span>
        </div>
        <div className="company-card-score">
          <span className="score-value">{score ?? "--"}</span>
          <span className="score-label">score</span>
        </div>
      </div>

      {/* Signal Summary */}
      <div className="company-card-signals">
        <div className="signal-row">
          <span className="signal-icon">💭</span>
          <span className="signal-text">{formatSignal(sentimentValue, "Sentiment")}</span>
        </div>
        <div className="signal-row">
          <span className="signal-icon">🚀</span>
          <span className="signal-text">{formatSignal(shippingValue, "Shipping")}</span>
        </div>
        <div className="signal-row">
          <span className="signal-icon">📈</span>
          <span className="signal-text">{formatSignal(marketValue, "Market")}</span>
        </div>
      </div>

      {/* Sparkline if available */}
      {mood?.history && mood.history.length > 1 && (
        <div className="company-card-trend">
          <span className="trend-label">30d trend</span>
          <Sparkline data={mood.history} color={company.color} width={100} height={24} />
        </div>
      )}

      {/* Summary */}
      {forecast?.summary && (
        <p className="company-card-summary">{forecast.summary}</p>
      )}

      {/* View Details hint */}
      <div className="company-card-footer">
        <span className="view-details">View Details →</span>
      </div>
    </motion.div>
  );
}
