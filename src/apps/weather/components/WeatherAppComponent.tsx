import { useState, useEffect, useCallback } from "react";
import type { AppProps } from "@/apps/base/types";
import { OverviewView } from "./Overview";
import { DetailView, DetailPanel } from "./Detail";
import type {
  ForecastData,
  MoodData,
  TimeframeType,
  ViewType,
  DetailPanelState,
  DetailType,
  Signals,
} from "../types/weather";
import { COMPANIES } from "../types/weather";
import "../styles/weather.css";

export function WeatherAppComponent({ instanceId: _instanceId }: AppProps) {
  // Data state
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [moods, setMoods] = useState<Record<string, MoodData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // View state
  const [view, setView] = useState<ViewType>("overview");
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<TimeframeType>("7d");
  const [detailPanel, setDetailPanel] = useState<DetailPanelState | null>(null);

  // Load data
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Load forecast
      const forecastRes = await fetch("/data/forecast.json");
      if (forecastRes.ok) {
        const forecastData = await forecastRes.json();
        setForecast(forecastData);
      } else {
        throw new Error("Failed to load forecast data");
      }

      // Load mood data for each company
      const moodData: Record<string, MoodData> = {};
      for (const company of COMPANIES) {
        try {
          const res = await fetch(`/data/mood/${company.id}.json`);
          if (res.ok) {
            moodData[company.id] = await res.json();
          }
        } catch (_e) {
          console.warn(`Failed to load mood for ${company.id}`);
        }
      }
      setMoods(moodData);

      setLoading(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load weather data");
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // View handlers
  const handleCompanyClick = (companyId: string) => {
    setSelectedCompany(companyId);
    setView("detail");
  };

  const handleBackToOverview = () => {
    setView("overview");
    setSelectedCompany(null);
  };

  const handleDetailClick = (detailType: DetailType, signals: Signals) => {
    if (selectedCompany) {
      setDetailPanel({
        type: detailType,
        company: selectedCompany,
        signals,
      });
    }
  };

  const handleCloseDetailPanel = () => {
    setDetailPanel(null);
  };

  const handleTimeframeChange = (newTimeframe: TimeframeType) => {
    setTimeframe(newTimeframe);
    // Future: reload data for different timeframe
  };

  const handleRefresh = () => {
    loadData();
  };

  // Loading state
  if (loading) {
    return (
      <div className="weather-app">
        <div className="weather-loading">
          <div className="weather-loading-spinner" />
          <span className="weather-loading-text">Loading forecast...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="weather-app">
        <div className="weather-error">
          <span className="weather-error-text">{error}</span>
          <button className="weather-error-button" onClick={handleRefresh}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Determine if current view is stormy
  const currentCompanyForecast = selectedCompany ? forecast?.forecast?.[selectedCompany] : null;
  const isStormy = currentCompanyForecast?.weather === "stormy";

  return (
    <div className={`weather-app ${isStormy ? "stormy" : ""}`}>
      {view === "overview" ? (
        <OverviewView
          forecast={forecast?.forecast}
          moods={moods}
          lastUpdated={forecast?.lastUpdated}
          timeframe={timeframe}
          onTimeframeChange={handleTimeframeChange}
          onCompanyClick={handleCompanyClick}
          onRefresh={handleRefresh}
        />
      ) : (
        <DetailView
          companyId={selectedCompany || "anthropic"}
          forecast={currentCompanyForecast || undefined}
          mood={selectedCompany ? moods[selectedCompany] : undefined}
          lastUpdated={forecast?.lastUpdated}
          onBack={handleBackToOverview}
          onDetailClick={handleDetailClick}
        />
      )}

      {/* Detail Panel Overlay */}
      <DetailPanel detailPanel={detailPanel} onClose={handleCloseDetailPanel} />
    </div>
  );
}
