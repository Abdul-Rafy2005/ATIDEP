import { useState, useEffect } from 'react';
import { Spotlight } from '@/components/ui/spotlight';
import { ArrowUpRight, ArrowRight } from 'lucide-react';
import type { OverviewMetrics, RunItem } from '../types';
import { fallbackOverview, fallbackRuns } from '../data/fallback';

interface OverviewViewProps {
  onNavigateTab: (tab: string) => void;
}

interface RadarTacticData {
  id: string;
  name: string;
  coverage: number; // 0 - 100
  adversary: number; // 0 - 100
  coveredCount: number;
  totalCount: number;
  techniques: string;
}

// 14 MITRE ATT&CK Tactics in exact clockwise order matching user reference image
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

export const OverviewView = ({ onNavigateTab }: OverviewViewProps) => {
  const [metrics, setMetrics] = useState<OverviewMetrics>(fallbackOverview);
  const [runs, setRuns] = useState<RunItem[]>(fallbackRuns);
  const [selectedTactic, setSelectedTactic] = useState<RadarTacticData>(radarTactics[3]); // Default to TA0002 Execution

  useEffect(() => {
    fetch('/api/overview')
      .then(res => res.ok ? res.json() : null)
      .then(data => { if (data) setMetrics(data); })
      .catch(() => {});

    fetch('/api/runs')
      .then(res => res.ok ? res.json() : null)
      .then(data => { if (data && data.length) setRuns(data); })
      .catch(() => {});
  }, []);

  // Spider web geometry parameters
  const cx = 200;
  const cy = 200;
  const maxR = 135;
  const levels = [0.25, 0.5, 0.75, 1.0];
  const numTactics = radarTactics.length;

  // Compute vertex coordinates for polygon webs
  const getCoordinates = (value: number, index: number) => {
    const angle = (index * 2 * Math.PI) / numTactics - Math.PI / 2;
    const r = (maxR * value) / 100;
    return {
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    };
  };

  const getLabelCoordinates = (index: number) => {
    const angle = (index * 2 * Math.PI) / numTactics - Math.PI / 2;
    const r = maxR + 25;
    return {
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    };
  };

  // Build polygon path strings
  const coveragePoints = radarTactics
    .map((t, i) => {
      const { x, y } = getCoordinates(t.coverage, i);
      return `${x},${y}`;
    })
    .join(' ');

  const adversaryPoints = radarTactics
    .map((t, i) => {
      const { x, y } = getCoordinates(t.adversary, i);
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <div className="w-full space-y-6">
      {/* Ambient Spotlight Hero Banner */}
      <div className="relative rounded-xl bg-slate-950 p-6 md:p-8 text-white overflow-hidden shadow-sm border border-slate-800">
        <Spotlight className="-top-36 left-10 md:left-60 md:-top-20" fill="#2563eb" />
        <div className="relative z-10 max-w-3xl space-y-2.5">
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-slate-800/80 border border-slate-700 text-[11px] font-mono text-slate-300">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
            <span>ATIDEP Enterprise Detection Engine</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
            Automated Threat-Informed Detection Engineering Platform
          </h1>
          <p className="text-xs md:text-sm text-slate-400 leading-relaxed max-w-2xl">
            Autonomous extraction of attacker behavior from raw CTI, local LLM Sigma rule generation, 
            and multi-point functional verification against synthetic process creation logs.
          </p>
          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={() => onNavigateTab('pipeline')}
              className="px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <span>Launch Pipeline Studio</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onNavigateTab('coverage')}
              className="px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold transition-all cursor-pointer"
            >
              Inspect ATT&CK Matrix
            </button>
          </div>
        </div>
      </div>

      {/* KPI Metrics Ribbon (Restrained, Unified Corporate Palette) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Techniques Tracked</span>
            <span className="text-[10px] font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-semibold">Sets 1-3</span>
          </div>
          <div className="flex items-baseline justify-between mt-2">
            <div className="text-3xl font-extrabold text-slate-900 font-mono">{metrics.total_techniques}</div>
            <div className="text-xs font-semibold text-slate-500 font-mono">100% Target Scope</div>
          </div>
          <div className="text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100 flex items-center justify-between">
            <span>44 unique attack patterns</span>
            <span className="text-slate-700 font-bold font-mono">14 Tactics</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Strict Verified</span>
            <span className="text-[10px] font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded font-mono">No Evasion</span>
          </div>
          <div className="flex items-baseline justify-between mt-2">
            <div className="text-3xl font-extrabold text-slate-900 font-mono">{metrics.covered}</div>
            <div className="text-xs font-bold text-blue-700 font-mono">+12.5% vs v1</div>
          </div>
          <div className="text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100 flex items-center justify-between">
            <span>Passed shown + hidden variant</span>
            <span className="text-slate-700 font-semibold font-mono">Generalizable</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Strict Coverage Ratio</span>
            <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 font-mono">Validated</span>
          </div>
          <div className="flex items-baseline justify-between mt-2">
            <div className="text-3xl font-extrabold text-blue-700 font-mono">{metrics.coverage_pct}%</div>
            <div className="text-xs font-semibold text-slate-500 font-mono">Target: &gt;70%</div>
          </div>
          <div className="text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100 flex items-center justify-between">
            <span>Automated gate verified</span>
            <span className="text-slate-700 font-semibold font-mono">Empirical</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Evaluated Rules</span>
            <span className="text-[10px] font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-semibold">14 Batches</span>
          </div>
          <div className="flex items-baseline justify-between mt-2">
            <div className="text-3xl font-extrabold text-slate-900 font-mono">{metrics.total_rules_tested}</div>
            <div className="text-xs font-semibold text-slate-500 font-mono">RTX 4000 Ada</div>
          </div>
          <div className="text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100 flex items-center justify-between">
            <span>Offline local inference</span>
            <span className="text-slate-700 font-semibold font-mono">0 Cloud Calls</span>
          </div>
        </div>
      </div>

      {/* Middle Row: MITRE Spider Web Radar (Matching Image 2) + Model Benchmark */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full">
        {/* MITRE ATT&CK Spider Web Radar Panel (7 Cols) */}
        <div className="lg:col-span-7 bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h2 className="text-sm font-bold text-slate-900 tracking-tight">MITRE ATT&CK Tactic Radar Coverage</h2>
                <p className="text-xs text-slate-500">Multi-layer spider web comparing rule coverage against observed adversary activity</p>
              </div>
              <span className="text-[10px] font-mono font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                14 Tactics
              </span>
            </div>

            {/* Radar Header Legend (Identical to user's attached PNG) */}
            <div className="flex items-center justify-center gap-8 pt-4 pb-1 text-xs font-semibold font-sans">
              <div className="flex items-center gap-2 text-indigo-600">
                <span className="w-3.5 h-3 rounded-xs bg-indigo-500"></span>
                <span>Coverage</span>
              </div>
              <div className="flex items-center gap-2 text-rose-600">
                <span className="w-3.5 h-3 rounded-xs bg-rose-600"></span>
                <span>Adversaries (3)</span>
              </div>
            </div>

            {/* Spider Web SVG & Interactive Inspector */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
              {/* Spider Web Chart (Left 8 Cols) */}
              <div className="md:col-span-7 flex justify-center py-2">
                <svg viewBox="0 0 400 400" className="w-full max-w-[340px] select-none">
                  {/* Concentric 14-sided polygon web lines */}
                  {levels.map((level, lvlIdx) => {
                    const ringPoints = radarTactics
                      .map((_, i) => {
                        const { x, y } = getCoordinates(level * 100, i);
                        return `${x},${y}`;
                      })
                      .join(' ');
                    return (
                      <polygon
                        key={lvlIdx}
                        points={ringPoints}
                        fill="none"
                        stroke="#e2e8f0"
                        strokeWidth="1"
                      />
                    );
                  })}

                  {/* Radial spokes from center to each vertex */}
                  {radarTactics.map((_, i) => {
                    const angle = (i * 2 * Math.PI) / numTactics - Math.PI / 2;
                    const x2 = cx + maxR * Math.cos(angle);
                    const y2 = cy + maxR * Math.sin(angle);
                    return (
                      <line
                        key={i}
                        x1={cx}
                        y1={cy}
                        x2={x2}
                        y2={y2}
                        stroke="#e2e8f0"
                        strokeWidth="1"
                      />
                    );
                  })}

                  {/* Axis percentage labels along top spoke */}
                  <text x={cx + 3} y={cy - maxR * 0.25 - 2} fontSize="9" fill="#94a3b8" fontFamily="monospace" textAnchor="start">25%</text>
                  <text x={cx + 3} y={cy - maxR * 0.5 - 2} fontSize="9" fill="#94a3b8" fontFamily="monospace" textAnchor="start">50%</text>
                  <text x={cx + 3} y={cy - maxR * 0.75 - 2} fontSize="9" fill="#94a3b8" fontFamily="monospace" textAnchor="start">75%</text>
                  <text x={cx + 3} y={cy - 3} fontSize="9" fill="#94a3b8" fontFamily="monospace" textAnchor="start">0%</text>

                  {/* Adversary Observed Polygon (Red / Rose layer with blend) */}
                  <polygon
                    points={adversaryPoints}
                    fill="rgba(225, 29, 72, 0.22)"
                    stroke="#e11d48"
                    strokeWidth="1.5"
                  />

                  {/* Coverage Polygon (Blue / Indigo layer with blend) */}
                  <polygon
                    points={coveragePoints}
                    fill="rgba(79, 70, 229, 0.25)"
                    stroke="#4f46e5"
                    strokeWidth="1.5"
                  />

                  {/* Vertex nodes and clickable targets */}
                  {radarTactics.map((t, i) => {
                    const { x, y } = getCoordinates(t.coverage, i);
                    const isSelected = selectedTactic.id === t.id;
                    return (
                      <g key={i} onClick={() => setSelectedTactic(t)} className="cursor-pointer">
                        <circle
                          cx={x}
                          cy={y}
                          r={isSelected ? 5 : 3.5}
                          fill={isSelected ? '#1e1b4b' : '#4f46e5'}
                          stroke="#ffffff"
                          strokeWidth={isSelected ? 2 : 1.5}
                        />
                      </g>
                    );
                  })}

                  {/* Tactic ID Labels around the perimeter (TA0043, TA0042, etc.) */}
                  {radarTactics.map((t, i) => {
                    const { x, y } = getLabelCoordinates(i);
                    const isSelected = selectedTactic.id === t.id;
                    return (
                      <text
                        key={i}
                        x={x}
                        y={y}
                        fontSize="10"
                        fontWeight={isSelected ? '800' : '600'}
                        fontFamily="monospace"
                        fill={isSelected ? '#1e293b' : '#64748b'}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        onClick={() => setSelectedTactic(t)}
                        className="cursor-pointer hover:fill-blue-700 transition-colors"
                      >
                        {t.id}
                      </text>
                    );
                  })}
                </svg>
              </div>

              {/* Tactic Detail Inspector (Right 5 Cols - Fills user requirement for detail) */}
              <div className="md:col-span-5 bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                  <div>
                    <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider font-bold">Selected Tactic</span>
                    <div className="text-sm font-extrabold text-slate-900 font-mono mt-0.5 flex items-center gap-1.5">
                      <span>{selectedTactic.id}</span>
                      <span className="text-xs text-slate-600 font-sans font-semibold">({selectedTactic.name})</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
                    <span className="text-slate-500">Verified Rule Coverage:</span>
                    <span className="font-mono font-bold text-indigo-700">{selectedTactic.coverage}%</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
                    <span className="text-slate-500">Technique Ratio:</span>
                    <span className="font-mono font-bold text-slate-800">{selectedTactic.coveredCount} / {selectedTactic.totalCount} tested</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-slate-200/60">
                    <span className="text-slate-500">Observed Adversary Index:</span>
                    <span className="font-mono font-bold text-rose-600">{selectedTactic.adversary}%</span>
                  </div>
                  <div className="pt-1">
                    <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">Target Techniques:</span>
                    <div className="font-mono text-[11px] text-slate-700 bg-white p-2 rounded border border-slate-200 truncate">
                      {selectedTactic.techniques}
                    </div>
                  </div>
                </div>

                <div className="text-[10px] text-slate-400 italic">
                  * Click any tactic ID around the spider web to inspect.
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
            <span>Peak Coverage: Discovery (100%), Defense Evasion (80%), Execution (87.5%)</span>
            <button
              onClick={() => onNavigateTab('coverage')}
              className="text-blue-700 hover:text-blue-900 font-semibold cursor-pointer"
            >
              Open ATT&CK Matrix
            </button>
          </div>
        </div>

        {/* Set 3 Model Pass Benchmark (5 Cols, Unified Professional Blue Palette) */}
        <div className="lg:col-span-5 bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h2 className="text-sm font-bold text-slate-900 tracking-tight">Set 3 Final Locked Test Benchmark</h2>
                <p className="text-xs text-slate-500">Strict pass rate out of 60 trials across prompt revisions</p>
              </div>
              <span className="text-[10px] font-mono font-bold text-blue-800 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-200">
                Primary: 14b (v3b)
              </span>
            </div>

            {/* Clean Monochromatic Blue / Slate Progression */}
            <div className="py-5 space-y-4">
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1.5">
                  <span className="text-slate-900 font-mono font-bold">qwen2.5-coder:14b (v3b) [Primary Winner]</span>
                  <span className="text-slate-900 font-mono font-bold">57 / 60 (95.0%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                  <div className="bg-blue-600 h-3 rounded-full" style={{ width: '95%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1.5">
                  <span className="text-slate-700 font-mono">qwen2.5-coder:7b (v3a) [Comparison Model]</span>
                  <span className="text-slate-700 font-mono">54 / 60 (90.0%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                  <div className="bg-blue-500 h-3 rounded-full" style={{ width: '90%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1.5">
                  <span className="text-slate-600 font-mono">qwen2.5-coder:14b (v3a) [Exploratory Run]</span>
                  <span className="text-slate-600 font-mono">55 / 60 (91.7%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                  <div className="bg-blue-400 h-3 rounded-full" style={{ width: '91.7%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1.5">
                  <span className="text-slate-500 font-mono">qwen2.5-coder:14b (v1) [Baseline Zero-Shot]</span>
                  <span className="text-slate-500 font-mono">35 / 60 (58.3%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                  <div className="bg-slate-400 h-3 rounded-full" style={{ width: '58.3%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>Primary Strict Pass: 57/60</span>
            <span>Zero Syntax Failures</span>
          </div>
        </div>
      </div>

      {/* Lower Row: Full-Width Runs Table + Tactical Posture Vector Status */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full">
        {/* Recent Batches Table (8 Cols) */}
        <div className="lg:col-span-8 bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900 tracking-tight">Latest Evaluation Batches</h2>
              <p className="text-xs text-slate-500">Historical records of model evaluation batches verified against the synthetic gate</p>
            </div>
            <button
              onClick={() => onNavigateTab('runs')}
              className="text-xs font-semibold text-blue-700 hover:text-blue-900 flex items-center gap-1 cursor-pointer"
            >
              <span>View All 14 Runs</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="overflow-x-auto flex-1 w-full">
            <table className="w-full text-xs text-left font-mono">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold font-sans">
                  <th className="py-2.5 px-3">Run Folder</th>
                  <th className="py-2.5 px-3">Set</th>
                  <th className="py-2.5 px-3">Prompt</th>
                  <th className="py-2.5 px-3">Model</th>
                  <th className="py-2.5 px-3">Strict Pass</th>
                  <th className="py-2.5 px-3">Syntax Err</th>
                  <th className="py-2.5 px-3">Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {runs.slice(0, 5).map((r, i) => (
                  <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 px-3 font-bold text-slate-900">{r.folder}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-700">Set {r.set}</td>
                    <td className="py-2.5 px-3 text-blue-700 font-bold">{r.prompt}</td>
                    <td className="py-2.5 px-3 text-slate-600 truncate max-w-[120px]">{r.models[0].replace('qwen2.5-coder:', '')}</td>
                    <td className="py-2.5 px-3 font-bold text-slate-900">{r.strict_pass}/{r.total}</td>
                    <td className={`py-2.5 px-3 ${r.syntax_errors > 0 ? 'text-red-600 font-bold' : 'text-slate-400'}`}>{r.syntax_errors}</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-sans uppercase font-bold border ${
                        r.label === 'primary' ? 'bg-blue-50 text-blue-800 border-blue-200' :
                        'bg-slate-100 text-slate-700 border-slate-200'
                      }`}>
                        {r.label}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tactical Readiness by Vector (4 Cols - Uniform Professional Palette) */}
        <div className="lg:col-span-4 bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2">
              <h2 className="text-sm font-bold text-slate-900 tracking-tight">Tactical Posture by Vector</h2>
              <span className="text-[10px] font-mono text-slate-500 font-semibold">ATT&CK Matrix</span>
            </div>
            <div className="space-y-3.5 text-xs">
              <div>
                <div className="flex justify-between text-slate-700 font-medium mb-1">
                  <span>Execution (Process Creation)</span>
                  <span className="font-bold text-slate-900 font-mono">7 / 8 (87.5%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '87.5%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-slate-700 font-medium mb-1">
                  <span>Defense Evasion</span>
                  <span className="font-bold text-slate-900 font-mono">12 / 15 (80.0%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '80%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-slate-700 font-medium mb-1">
                  <span>Discovery</span>
                  <span className="font-bold text-slate-900 font-mono">6 / 6 (100.0%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '100%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-slate-700 font-medium mb-1">
                  <span>Persistence</span>
                  <span className="font-bold text-slate-900 font-mono">8 / 12 (66.7%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '66.7%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-slate-700 font-medium mb-1">
                  <span>Privilege Escalation</span>
                  <span className="font-bold text-slate-900 font-mono">4 / 5 (80.0%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '80%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 bg-slate-50 p-2.5 rounded-lg text-[11px] text-slate-600">
            <div className="flex items-center justify-between font-semibold">
              <span>Validation Engine</span>
              <span className="text-slate-800 font-mono font-bold">pySigma SQLite</span>
            </div>
            <div className="text-slate-500 mt-1">Multi-point: Syntax &and; Shown &and; Variant &and; Quiet</div>
          </div>
        </div>
      </div>
    </div>
  );
};
