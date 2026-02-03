import { BaseApp } from "../base/types";
import { WeatherAppComponent } from "./components/WeatherAppComponent";

export const appMetadata = {
  name: "AI Weather",
  version: "1.0.0",
  creator: {
    name: "AI Weather Report",
    url: "https://github.com/katehostetler/ai-weather-report",
  },
  github: "https://github.com/katehostetler/ai-weather-report",
  icon: "/icons/weather.png",
};

export const helpItems = [
  {
    icon: "",
    title: "Weather Overview",
    description: "See the current AI weather for all major companies at a glance",
  },
  {
    icon: "",
    title: "Signal Breakdown",
    description: "Click a company to see sentiment, shipping, market, and competitive signals",
  },
  {
    icon: "",
    title: "Peer Comparison",
    description: "See how each company performs relative to their peers",
  },
  {
    icon: "",
    title: "Recent Activity",
    description: "View recent blog posts and announcements from each company",
  },
];

export const WeatherApp: BaseApp = {
  id: "weather",
  name: "AI Weather",
  description: "Track the climate of artificial intelligence",
  icon: {
    type: "image",
    src: "/icons/weather.png",
  },
  component: WeatherAppComponent,
  helpItems,
  metadata: appMetadata,
};
