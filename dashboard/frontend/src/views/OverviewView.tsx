import { useState, useEffect } from 'react';
import type { OverviewMetrics, RunItem } from '../types';
import { fallbackOverview, fallbackRuns } from '../data/fallback';
import { MetricCard } from '../components/ui/metric-card';
import { getRoleBadgeStyle } from '../components/ui/verdict-badge';

interface OverviewViewProps {
  onNavigateTab: (tab: string) => void;
  onSelectRun?: (folder: string) => void;
}

interface RadarTacticData {
  id: string;
  name: string;
  coverage: number;
  adversary: number;
  coveredCount: number;
  totalCount: number;
  techniques: string;
}

const radarTactics: RadarTacticData[] = [
  { id: 'TA0043', name: 'Reconnaissance', coverage: 50, adversary: 75, coveredCount: 1, totalCount: 2, techniques: 'T1595, T1592' },
  { id: 'TA0042', name: 'Resource Development', coverage: 50, adversary: 90, coveredCount: 1, totalCount: 2, techniques: 'T1583, T1584' },
  { id: 'TA0001', name: 'Initial Access', coverage: 75, adversary: 75, coveredCount: 2, totalCount: 2, techniques: 'T1566, T1190' },
  { id: 'TA0002', name: 'Execution', coverage: 87.5, adversary: 90, coveredCount: 7, totalCount: 8, techniques: 'T1059.001, T1047, T1053.002, T1202' },
  { id: 'TA0003', name: 'Persistence', coverage: 66.7, adversary: 15, coveredCount: 8, totalCount: 12, techniques: 'T1547.001, T1053.005, T1136' },
  { id: 'TA0004', name: 'Privilege Escalation', coverage: 80, adversary: 20, coveredCount: 4, totalCount: 5, techniques: 'T1548, T1134, T1068' },
  { id: 'TA0005', name: 'Defense Evasion', coverage: 80, adversary: 95, coveredCount: 12, totalCount: 15, techniques: 'T1564.004, T1112, T1218, T1127' },
  { id: 'TA0006', name: 'Credential Access', coverage: 75, adversary: 90, coveredCount: 3, totalCount: 4, techniques: 'T1003.001, T1003.002, T1110' },
  { id: 'TA0007', name: 'Discovery', coverage: 100, adversary: 85, coveredCount: 6, totalCount: 6, techniques: 'T1615, T1082, T1049, T1016' },
  { id: 'TA0008', name: 'Lateral Movement', coverage: 66.7, adversary: 80, coveredCount: 2, totalCount: 3, techniques: 'T1021.002, T1021.006' },
  { id: 'TA0009', name: 'Collection', coverage: 50, adversary: 10, coveredCount: 1, totalCount: 2, techniques: 'T1113, T1123' },
  { id: 'TA0011', name: 'Command & Control', coverage: 75, adversary: 85, coveredCount: 3, totalCount: 4, techniques: 'T1071, T1090, T1572' },
  { id: 'TA0010', name: 'Exfiltration', coverage: 100, adversary: 15, coveredCount: 1, totalCount: 1, techniques: 'T1041' },
  { id: 'TA0040', name: 'Impact', coverage: 66.7, adversary: 20, coveredCount: 2, totalCount: 3, techniques: 'T1529, T1485, T1490' },
];

const shortTacticName: Record<string, string> = {
  'TA0043': 'Recon',
  'TA0042': 'Resource Dev',
  'TA0001': 'Initial Access',
  'TA0002': 'Execution',
  'TA0003': 'Persistence',
  'TA0004': 'Priv Esc',
  'TA0005': 'Def Evasion',
  'TA0006': 'Cred Access',
  'TA0007': 'Discovery',
  'TA0008': 'Lateral Mvmt',
  'TA0009': 'Collection',
  'TA0011': 'C2',
  'TA0010': 'Exfiltration',
  'TA0040': 'Impact',
};

export const OverviewView = ({ onNavigateTab, onSelectRun }: OverviewViewProps) => {
  const [metrics, setMetrics] = useState<OverviewMetrics>(fallbackOverview);
  const [runs, setRuns] = useState<RunItem[]>(fallbackRuns);
  const [loading, setLoading] = useState(true);
  const [selectedTactic, setSelectedTactic] = useState<RadarTacticData>(radarTactics[3]);

  useEffect(() => {
    Promise.all([
      fetch('/api/overview').then(res => res.ok ? res.json() : null).catch(() => null),
      fetch('/api/runs').then(res => res.ok ? res.json() : null).catch(() => null),
    ]).then(([overviewData, runsData]) => {
      if (overviewData) setMetrics(overviewData);
      if (runsData?.length) setRuns(runsData);
    }).finally(() => setLoading(false));
  }, []);

  const cx = 200;
  const cy = 200;
  const maxR = 135;
  const levels = [0.25, 0.5, 0.75, 1.0];
  const numTactics = radarTactics.length;

  const getCoordinates = (value: number, index: number) => {
    const angle = (index * 2 * Math.PI) / numTactics - Math.PI / 2;
    const r = (maxR * value) / 100;
    return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  };

  const getLabelCoordinates = (index: number) => {
    const angle = (index * 2 * Math.PI) / numTactics - Math.PI / 2;
    const r = maxR + 32;
    return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  };

  const coveragePoints = radarTactics
    .map((t, i) => { const { x, y } = getCoordinates(t.coverage, i); return `${x},${y}`; })
    .join(' ');

  const adversaryPoints = radarTactics
    .map((t, i) => { const { x, y } = getCoordinates(t.adversary, i); return `${x},${y}`; })
    .join(' ');

  return (
    <div className="w-full space-y-4">
      {/* Project header */}
      <div className="rounded-xl bg-brand-muted border border-brand-edge p-5 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-brand/5 to-transparent pointer-events-none" />
        <div className="relative">
          <h1 className="text-lg font-bold tracking-tight text-fg">
            Automated Threat-Informed Detection Engineering
          </h1>
          <p className="text-xs text-fg-secondary mt-1.5 leading-relaxed max-w-xl">
            Local LLM Sigma rule generation with multi-point synthetic log validation.
            44 techniques across 14 MITRE ATT&CK tactics, evaluated offline on Ollama.
          </p>
          <div className="flex gap-2.5 mt-4">
            <button onClick={() => onNavigateTab('pipeline')}
              className="px-4 py-2 rounded-lg bg-brand hover:bg-brand-hover text-brand-fg text-xs font-semibold transition-all duration-150 cursor-pointer shadow-sm hover:shadow-md">
              Pipeline Studio
            </button>
            <button onClick={() => onNavigateTab('coverage')}
              className="px-4 py-2 rounded-lg bg-panel hover:bg-panel-hover border border-edge text-fg-secondary text-xs font-semibold transition-all duration-150 cursor-pointer">
              ATT&CK Coverage
            </button>
          </div>
        </div>
      </div>

      {/* KPI metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 w-full">
        <MetricCard label="Techniques tracked" value={metrics.total_techniques} detail="Across sets 1, 2, and 3" className={loading ? 'animate-pulse' : ''} />
        <MetricCard label="Strict verified" value={metrics.covered} detail="Passed shown + variant" className={loading ? 'animate-pulse' : ''} />
        <MetricCard label="Coverage rate" value={`${metrics.coverage_pct}%`} detail="Of tracked techniques" className={loading ? 'animate-pulse' : ''} />
        <MetricCard label="Rules evaluated" value={metrics.total_rules_tested} detail="Local Ollama inference" className={loading ? 'animate-pulse' : ''} />
      </div>

      {/* Radar + Benchmark */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 w-full">
        <div className="lg:col-span-7 bg-panel p-4 rounded-lg border border-edge">
          <div className="flex items-center justify-between pb-2.5 border-b border-subtle">
            <div>
              <h2 className="text-sm font-semibold text-fg">MITRE ATT&CK Tactic Coverage</h2>
              <p className="text-[11px] text-fg-muted">Rule coverage vs. observed adversary activity</p>
            </div>
          </div>

          <div className="flex items-center justify-center gap-5 pt-2.5 pb-1 text-[11px] text-fg-secondary">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-1.5 rounded-sm bg-brand"></span>
              <span>Coverage</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-1.5 rounded-sm bg-critical"></span>
              <span>Adversary activity</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
            <div className="md:col-span-7 flex justify-center py-2">
              <svg viewBox="0 0 400 400" className="w-full max-w-[340px] select-none">
                {levels.map((level, lvlIdx) => {
                  const ringPoints = radarTactics
                    .map((_, i) => { const { x, y } = getCoordinates(level * 100, i); return `${x},${y}`; })
                    .join(' ');
                  return <polygon key={lvlIdx} points={ringPoints} fill="none" stroke="var(--edge)" strokeWidth="1" />;
                })}

                {radarTactics.map((_, i) => {
                  const angle = (i * 2 * Math.PI) / numTactics - Math.PI / 2;
                  return (
                    <line key={i} x1={cx} y1={cy}
                      x2={cx + maxR * Math.cos(angle)} y2={cy + maxR * Math.sin(angle)}
                      stroke="var(--edge)" strokeWidth="1" />
                  );
                })}

                <text x={cx + 3} y={cy - maxR * 0.25 - 2} fontSize="9" fill="var(--fg-muted)" fontFamily="monospace" textAnchor="start">25%</text>
                <text x={cx + 3} y={cy - maxR * 0.5 - 2} fontSize="9" fill="var(--fg-muted)" fontFamily="monospace" textAnchor="start">50%</text>
                <text x={cx + 3} y={cy - maxR * 0.75 - 2} fontSize="9" fill="var(--fg-muted)" fontFamily="monospace" textAnchor="start">75%</text>
                <text x={cx + 3} y={cy - 3} fontSize="9" fill="var(--fg-muted)" fontFamily="monospace" textAnchor="start">0%</text>

                <polygon points={adversaryPoints} fill="var(--critical)" fillOpacity="0.15" stroke="var(--critical)" strokeWidth="1.5" />
                <polygon points={coveragePoints} fill="var(--brand)" fillOpacity="0.18" stroke="var(--brand)" strokeWidth="1.5" />

                {radarTactics.map((t, i) => {
                  const { x, y } = getCoordinates(t.coverage, i);
                  const isSelected = selectedTactic.id === t.id;
                  return (
                    <g key={i} onClick={() => setSelectedTactic(t)} className="cursor-pointer">
                      <circle cx={x} cy={y}
                        r={isSelected ? 5 : 3.5}
                        fill="var(--brand)"
                        stroke="var(--panel)" strokeWidth={isSelected ? 2 : 1.5} />
                    </g>
                  );
                })}

                {radarTactics.map((t, i) => {
                  const { x, y } = getLabelCoordinates(i);
                  const isSelected = selectedTactic.id === t.id;
                  return (
                    <text key={i} x={x} y={y}
                      fontSize="9" fontWeight={isSelected ? '700' : '500'}
                      fontFamily="var(--font-sans)"
                      fill={isSelected ? 'var(--brand)' : 'var(--fg-muted)'}
                      textAnchor="middle" dominantBaseline="middle"
                      onClick={() => setSelectedTactic(t)}
                      className="cursor-pointer"
                      style={{ transition: 'fill 150ms' }}>
                      {shortTacticName[t.id] || t.id}
                    </text>
                  );
                })}
              </svg>
            </div>

            <div className="md:col-span-5 bg-panel-inset p-3.5 rounded-lg border border-edge space-y-2.5">
              <div className="pb-2 border-b border-subtle">
                <div className="text-[10px] text-fg-muted">Selected tactic</div>
                <div className="text-sm font-semibold text-fg mt-0.5">
                  {selectedTactic.id} <span className="font-normal text-fg-secondary">({selectedTactic.name})</span>
                </div>
              </div>

              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between items-center py-0.5">
                  <span className="text-fg-muted">Coverage</span>
                  <span className="font-mono font-semibold text-brand">{selectedTactic.coverage}%</span>
                </div>
                <div className="flex justify-between items-center py-0.5">
                  <span className="text-fg-muted">Techniques</span>
                  <span className="font-mono font-semibold text-fg">{selectedTactic.coveredCount}/{selectedTactic.totalCount}</span>
                </div>
                <div className="flex justify-between items-center py-0.5">
                  <span className="text-fg-muted">Adversary index</span>
                  <span className="font-mono font-semibold text-critical">{selectedTactic.adversary}%</span>
                </div>
                <div className="pt-1">
                  <div className="text-[10px] text-fg-muted mb-1">Techniques</div>
                  <div className="font-mono text-[11px] text-fg-secondary bg-panel p-2 rounded border border-edge truncate">
                    {selectedTactic.techniques}
                  </div>
                </div>
              </div>

              <div className="text-[10px] text-fg-muted">
                Click any tactic on the radar to inspect.
              </div>
            </div>
          </div>

          <div className="pt-2.5 border-t border-subtle flex items-center justify-between text-[11px] text-fg-muted">
            <span>Peak: Discovery (100%), Execution (87.5%)</span>
            <button onClick={() => onNavigateTab('coverage')}
              className="text-brand hover:text-brand-hover font-medium cursor-pointer">
              Open ATT&CK Matrix
            </button>
          </div>
        </div>

        {/* Set 3 Benchmark */}
        <div className="lg:col-span-5 bg-panel p-4 rounded-lg border border-edge flex flex-col justify-between">
          <div>
            <div className="pb-2.5 border-b border-subtle">
              <h2 className="text-sm font-semibold text-fg">Set 3 Locked Test Results</h2>
              <p className="text-[11px] text-fg-muted">Strict pass rate across prompt revisions (60 trials each)</p>
            </div>

            <div className="py-4 space-y-3.5">
              {[
                { label: '14b (v3b)', tag: 'Primary', score: '57/60 (95.0%)', pct: 95, barClass: 'bg-brand' },
                { label: '7b (v3a)', tag: 'Comparison', score: '58/60 (96.7%)', pct: 96.7, barClass: 'bg-bar-secondary' },
                { label: '14b (v3a)', tag: 'Exploratory', score: '55/60 (91.7%)', pct: 91.7, barClass: 'bg-bar-tertiary' },
                { label: '14b (v1)', tag: 'Baseline', score: '82/120 (68.3%)', pct: 68.3, barClass: 'bg-edge-hover' },
              ].map((m) => (
                <div key={m.label}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-fg-secondary font-medium">
                      {m.label} {m.tag === 'Primary' && <span className="text-brand font-semibold">{m.tag}</span>}
                      {m.tag !== 'Primary' && <span className="text-fg-muted">{m.tag}</span>}
                    </span>
                    <span className="font-mono font-semibold text-fg">{m.score}</span>
                  </div>
                  <div className="w-full bg-panel-inset rounded-full h-2 overflow-hidden">
                    <div className={`${m.barClass} h-2 rounded-full transition-all duration-500`} style={{ width: `${m.pct}%` }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-2.5 border-t border-subtle text-[11px] text-fg-muted">
            Primary (14b v3b): 57/60 strict pass, zero syntax failures
          </div>
        </div>
      </div>

      {/* Runs table + Tactic coverage */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 w-full">
        <div className="lg:col-span-8 bg-panel rounded-lg border border-edge overflow-hidden flex flex-col">
          <div className="p-3.5 border-b border-subtle flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-fg">Recent Evaluation Runs</h2>
              <p className="text-[11px] text-fg-muted">Model evaluation batches verified against the synthetic gate</p>
            </div>
            <button onClick={() => onNavigateTab('runs')}
              className="text-[11px] font-medium text-brand hover:text-brand-hover cursor-pointer">
              View all
            </button>
          </div>
          <div className="overflow-x-auto flex-1 w-full">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="bg-panel-inset border-b border-edge text-fg-muted font-medium">
                  <th className="py-2 px-3">Run</th>
                  <th className="py-2 px-3">Set</th>
                  <th className="py-2 px-3">Prompt</th>
                  <th className="py-2 px-3">Model</th>
                  <th className="py-2 px-3">Strict</th>
                  <th className="py-2 px-3">Errors</th>
                  <th className="py-2 px-3">Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-subtle">
                {runs.slice(0, 5).map((r, i) => (
                  <tr key={i}
                    onClick={() => { if (onSelectRun) onSelectRun(r.folder); onNavigateTab('runs'); }}
                    className="hover:bg-panel-hover cursor-pointer transition-colors">
                    <td className="py-2 px-3 font-mono font-medium text-fg text-[11px]">{r.folder}</td>
                    <td className="py-2 px-3 text-fg-secondary">Set {r.set}</td>
                    <td className="py-2 px-3 text-brand font-medium">{r.prompt}</td>
                    <td className="py-2 px-3 text-fg-secondary truncate max-w-[120px]">{r.models[0].replace('qwen2.5-coder:', '')}</td>
                    <td className="py-2 px-3 font-mono font-medium text-fg">{r.strict_pass}/{r.total}</td>
                    <td className={`py-2 px-3 font-mono ${r.syntax_errors > 0 ? 'text-critical font-semibold' : 'text-fg-muted'}`}>{r.syntax_errors}</td>
                    <td className="py-2 px-3">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border ${getRoleBadgeStyle(r.label)}`}>
                        {r.label}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="lg:col-span-4 bg-panel p-4 rounded-lg border border-edge">
          <div className="mb-2.5 pb-2 border-b border-subtle">
            <h2 className="text-sm font-semibold text-fg">Tactic Coverage</h2>
            <p className="text-[11px] text-fg-muted">Top 5 tactical categories</p>
          </div>
          <div className="space-y-3 text-xs">
            {[
              { name: 'Execution', covered: 7, total: 8, pct: 87.5 },
              { name: 'Defense Evasion', covered: 12, total: 15, pct: 80.0 },
              { name: 'Discovery', covered: 6, total: 6, pct: 100.0 },
              { name: 'Persistence', covered: 8, total: 12, pct: 66.7 },
              { name: 'Privilege Escalation', covered: 4, total: 5, pct: 80.0 },
            ].map((t) => (
              <div key={t.name}>
                <div className="flex justify-between text-fg-secondary mb-1">
                  <span>{t.name}</span>
                  <span className="font-mono font-medium text-fg">{t.covered}/{t.total} ({t.pct}%)</span>
                </div>
                <div className="w-full bg-panel-inset rounded-full h-1.5 overflow-hidden">
                  <div className="bg-brand h-1.5 rounded-full" style={{ width: `${t.pct}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
