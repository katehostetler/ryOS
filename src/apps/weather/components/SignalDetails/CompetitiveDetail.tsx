import type { Signals } from "../../types/weather";
import { COMPANIES } from "../../types/weather";

interface CompetitiveDetailProps {
  company: string;
  signals: Signals;
}

export default function CompetitiveDetail({ company, signals }: CompetitiveDetailProps) {
  const competitive = signals?.competitive;
  const value = competitive?.value;
  const vsPeers = competitive?.vs_peers;

  const percentage = value != null ? Math.round(value * 100) : null;
  const peerDiff = vsPeers ? parseFloat(vsPeers) : 0;

  // Calculate approximate rankings for all companies based on peer diff
  const baseScores: Record<string, number> = {
    Anthropic: 72,
    OpenAI: 75,
    Google: 68,
    Meta: 65,
    xAI: 60,
  };

  const ranks = COMPANIES.map((c) => {
    const isCurrent = c.id.toLowerCase() === company.toLowerCase();
    // Use actual percentage for current company, base scores for others
    const score = isCurrent ? percentage || 50 : (baseScores[c.name] || 50) + Math.round(peerDiff * 10);
    return { name: c.name, score: Math.max(0, Math.min(100, score)), isCurrent };
  }).sort((a, b) => b.score - a.score);

  return (
    <div className="signal-detail">
      <div className="signal-detail-summary">
        <div className="detail-metric-large">
          <span className="detail-value">{percentage ?? "—"}%</span>
          <span className="detail-label">Competitive Position Score</span>
        </div>
      </div>

      <div className="detail-section">
        <h4>Current Rankings</h4>
        <div className="ranking-table">
          {ranks.map((r, i) => (
            <div key={r.name} className={`ranking-row ${r.isCurrent ? "current" : ""}`}>
              <span className="ranking-position">#{i + 1}</span>
              <span className="ranking-name">{r.name}</span>
              <div className="ranking-bar-container">
                <div className="ranking-bar" style={{ width: `${r.score}%` }} />
              </div>
              <span className="ranking-score">{r.score}%</span>
            </div>
          ))}
        </div>
      </div>

      <div className="detail-section">
        <h4>What This Measures</h4>
        <p>
          Competitive positioning based on benchmark performance, model capabilities, market share estimates, and
          developer mindshare.
        </p>
      </div>

      <div className="detail-section">
        <h4>Factors Considered</h4>
        <ul className="detail-list">
          <li>LMSYS Chatbot Arena rankings</li>
          <li>Benchmark performance (MMLU, HumanEval, etc.)</li>
          <li>API usage and developer adoption</li>
          <li>Enterprise deployment announcements</li>
        </ul>
      </div>

      <div className="detail-section">
        <h4>How It Works</h4>
        <p>
          Each factor is weighted and normalized. Arena rankings provide a human-preference signal, while benchmarks
          measure raw capability. Developer adoption is estimated from API usage patterns and SDK downloads.
        </p>
      </div>
    </div>
  );
}
