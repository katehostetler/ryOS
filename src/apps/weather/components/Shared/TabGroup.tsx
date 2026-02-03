import { motion } from "framer-motion";

export interface Tab {
  id: string;
  label: string;
}

interface TabGroupProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  isStormy?: boolean;
}

export default function TabGroup({ tabs, activeTab, onTabChange, isStormy = false }: TabGroupProps) {
  return (
    <div className={`tab-group ${isStormy ? "stormy" : ""}`}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={`tab-item ${activeTab === tab.id ? "active" : ""}`}
          onClick={() => onTabChange(tab.id)}
        >
          {activeTab === tab.id && (
            <motion.div
              className="tab-indicator"
              layoutId="tab-indicator"
              transition={{ type: "spring", bounce: 0.2, duration: 0.4 }}
            />
          )}
          <span className="tab-label">{tab.label}</span>
        </button>
      ))}
    </div>
  );
}
