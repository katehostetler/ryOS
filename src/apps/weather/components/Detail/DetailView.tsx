import { motion } from "framer-motion";
import { WeatherIcon, SignalBreakdown, Sparkline } from "../Shared";
import type { CompanyForecast, MoodData, WeatherType, DetailType, Signals } from "../../types/weather";
import { COMPANIES } from "../../types/weather";

interface DetailViewProps {
  companyId: string;
  forecast?: CompanyForecast;
  mood?: MoodData;
  lastUpdated: string | undefined;
  onBack: () => void;
  onDetailClick: (detailType: DetailType, signals: Signals) => void;
}

export default function DetailView({
  companyId,
  forecast,
  mood,
  lastUpdated,
  onBack,
  onDetailClick,
}: DetailViewProps) {
  const company = COMPANIES.find((c) => c.id === companyId) || COMPANIES[0];
  const weather = (forecast?.weather || "foggy") as WeatherType;
  const score = forecast?.score ? Math.round(forecast.score * 100) : null;
  const isStormy = weather === "stormy";

  const handleDetailClick = (detailType: DetailType) => {
    if (forecast?.signals) {
      onDetailClick(detailType, forecast.signals);
    }
  };

  return (
    <div className={`detail-view ${isStormy ? "stormy" : ""}`}>
      {/* Header */}
      <div className="detail-view-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Forecast Summary
        </button>
      </div>

      {/* Company Hero */}
      <motion.div
        className="detail-hero"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="detail-hero-icon">
          <WeatherIcon weather={weather} size="large" animated />
        </div>
        <div className="detail-hero-info">
          <h1>{company.name}</h1>
          <div className="detail-hero-weather">
            <span className="weather-label">{forecast?.weather_info?.label || "Unknown"}</span>
            <span className="weather-description">{forecast?.weather_info?.description}</span>
          </div>
          <div className="detail-hero-score">
            <span className="score-value">{score ?? "--"}</span>
            <span className="score-label">Overall Score</span>
          </div>
        </div>
      </motion.div>

      {/* Summary */}
      {forecast?.summary && (
        <motion.div
          className="detail-summary"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <p>{forecast.summary}</p>
        </motion.div>
      )}

      {/* Main Content Grid */}
      <div className="detail-content">
        {/* Left Column: Signals */}
        <motion.div
          className="detail-signals"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2>Signal Breakdown</h2>
          <SignalBreakdown
            signals={forecast?.signals || null}
            isStormy={isStormy}
            company={company.name}
            onDetailClick={handleDetailClick}
          />
        </motion.div>

        {/* Right Column: Activity & Charts */}
        <div className="detail-sidebar">
          {/* Trend Chart */}
          {mood?.history && mood.history.length > 1 && (
            <motion.div
              className="detail-chart"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h3>30-Day Sentiment Trend</h3>
              <div className="chart-container">
                <Sparkline data={mood.history} color={company.color} width={280} height={80} />
              </div>
            </motion.div>
          )}

          {/* Recent Activity */}
          {mood?.posts && mood.posts.length > 0 && (
            <motion.div
              className="detail-activity"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h3>Recent Activity</h3>
              <div className="activity-list">
                {mood.posts.slice(0, 5).map((post, i) => (
                  <a
                    key={i}
                    href={post.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="activity-item"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <span className="activity-title">{post.title}</span>
                    {post.date && <span className="activity-date">{post.date}</span>}
                  </a>
                ))}
              </div>
            </motion.div>
          )}

          {/* Sentiment Badge */}
          {mood?.sentiment && (
            <motion.div
              className="detail-sentiment"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h3>Content Sentiment</h3>
              <div className="sentiment-badge-container">
                <span className={`sentiment-badge ${mood.sentiment.label.toLowerCase()}`}>
                  {mood.sentiment.label}
                </span>
                <span className="sentiment-score">{Math.round(mood.sentiment.score * 100)}%</span>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="detail-footer">
        {lastUpdated && (
          <span className="last-updated">Last updated: {new Date(lastUpdated).toLocaleString()}</span>
        )}
      </div>
    </div>
  );
}
