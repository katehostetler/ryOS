// Company definitions
export interface Company {
  id: string;
  name: string;
  color: string;
}

export const COMPANIES: Company[] = [
  { id: "anthropic", name: "Anthropic", color: "#D97706" },
  { id: "openai", name: "OpenAI", color: "#10B981" },
  { id: "google", name: "Google", color: "#3B82F6" },
  { id: "meta", name: "Meta", color: "#8B5CF6" },
  { id: "xai", name: "xAI", color: "#1DA1F2" },
];

// Weather types
export type WeatherType = "sunny" | "partly_cloudy" | "cloudy" | "rainy" | "stormy" | "foggy";

export type TimeframeType = "7d" | "14d" | "30d";

// Signal data
export interface Signal {
  value: number | null;
  vs_peers: string | null;
}

export interface Signals {
  sentiment: Signal;
  shipping: Signal;
  market: Signal;
  competitive: Signal;
}

// Weather info from forecast
export interface WeatherInfo {
  icon: string;
  emoji: string;
  label: string;
  description: string;
}

// Company forecast data
export interface CompanyForecast {
  weather: WeatherType;
  weather_info: WeatherInfo;
  score: number;
  signals: Signals;
  summary: string;
}

// Full forecast data structure
export interface ForecastData {
  lastUpdated: string;
  forecast: Record<string, CompanyForecast>;
}

// Multi-timeframe forecast structure (future enhancement)
export interface MultiTimeframeForecast {
  lastUpdated: string;
  "7d": { forecast: Record<string, CompanyForecast> };
  "14d": { forecast: Record<string, CompanyForecast> };
  "30d": { forecast: Record<string, CompanyForecast> };
}

// Mood/activity data
export interface MoodPost {
  title: string;
  date: string;
  url: string;
  summary?: string;
}

export interface MoodSentiment {
  label: string;
  score: number;
}

export interface MoodData {
  sentiment?: MoodSentiment;
  posts?: MoodPost[];
  history?: number[];
}

// Detail panel types
export type DetailType = "sentiment" | "shipping" | "market" | "competitive";

export interface DetailPanelState {
  type: DetailType;
  company: string;
  signals: Signals;
}

// View state
export type ViewType = "overview" | "detail";

export interface WeatherViewState {
  view: ViewType;
  selectedCompany: string | null;
  timeframe: TimeframeType;
}

// Signal configuration for display
export interface SignalConfig {
  label: string;
  icon: string;
  description: string;
  timeWindow: string;
  detailType: DetailType;
}

export const SIGNAL_CONFIG: Record<keyof Signals, SignalConfig> = {
  sentiment: {
    label: "Sentiment",
    icon: "message-circle",
    description: "Blog & HackerNews mood",
    timeWindow: "7-day window",
    detailType: "sentiment",
  },
  shipping: {
    label: "Shipping",
    icon: "rocket",
    description: "Release velocity",
    timeWindow: "14-day activity",
    detailType: "shipping",
  },
  market: {
    label: "Market",
    icon: "trending-up",
    description: "Stock momentum",
    timeWindow: "30-day trend",
    detailType: "market",
  },
  competitive: {
    label: "Competitive",
    icon: "trophy",
    description: "Benchmark ranking",
    timeWindow: "Current standings",
    detailType: "competitive",
  },
};

// Weather styling
export interface WeatherStyle {
  bg: string;
  icon: string;
  glow: string;
}

export const WEATHER_STYLES: Record<WeatherType, WeatherStyle> = {
  sunny: { bg: "from-amber-400 to-orange-500", icon: "sun", glow: "shadow-amber-400/50" },
  partly_cloudy: { bg: "from-teal-400 to-cyan-500", icon: "cloud-sun", glow: "shadow-teal-400/50" },
  cloudy: { bg: "from-gray-400 to-slate-500", icon: "cloud", glow: "shadow-gray-400/50" },
  rainy: { bg: "from-blue-400 to-indigo-500", icon: "cloud-rain", glow: "shadow-blue-400/50" },
  stormy: { bg: "from-red-400 to-rose-500", icon: "cloud-lightning", glow: "shadow-red-400/50" },
  foggy: { bg: "from-gray-300 to-gray-400", icon: "cloud-fog", glow: "shadow-gray-300/50" },
};
