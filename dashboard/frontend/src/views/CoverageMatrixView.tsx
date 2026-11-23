import { useState, useEffect } from 'react';
import type { TechniqueItem } from '../types';
import { fallbackTechniques } from '../data/fallback';
import { ExternalLink, Play, Search, ShieldCheck, CheckCircle2, AlertTriangle, Terminal, Copy, Check, Filter } from 'lucide-react';

interface CoverageMatrixViewProps {
  onNavigateTab: (tab: string) => void;
  searchFilter?: string;
}

const tacticOrder = [
  'Initial Access', 'Execution', 'Persistence', 'Privilege Escalation',
  'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
  'Collection', 'Command and Control', 'Exfiltration', 'Impact',
  'Resource Development', 'Reconnaissance'
];

export const CoverageMatrixView = ({ onNavigateTab, searchFilter = '' }: CoverageMatrixViewProps) => {
  const [techniques, setTechniques] = useState<TechniqueItem[]>(fallbackTechniques);
  const [selectedSet, setSelectedSet] = useState<string>('all');
  const [selectedVerdict, setSelectedVerdict] = useState<string>('all');
  const [search, setSearch] = useState<string>(searchFilter);
  const [selectedId, setSelectedId] = useState<string>('T1059.001');
  const [copiedRule, setCopiedRule] = useState<boolean>(false);

  useEffect(() => {
    fetch('/api/techniques')
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data && data.length) {
          setTechniques(data);
          if (!data.some((t: TechniqueItem) => t.id === selectedId)) {
            setSelectedId(data[0].id);
          }
        }
      })
      .catch(() => {});
  }, []);

  const selectedTech = techniques.find(t => t.id === selectedId) || techniques[0] || fallbackTechniques[0];

  const filtered = techniques.filter(t => {
    if (selectedSet !== 'all' && !t.sets.includes(parseInt(selectedSet))) return false;
    if (selectedVerdict !== 'all' && t.best_verdict !== selectedVerdict) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      const matchId = t.id.toLowerCase().includes(q);
      const matchTitle = (t.title || '').toLowerCase().includes(q);
      const matchTactic = t.tactics.some(tac => tac.toLowerCase().includes(q));
      if (!matchId && !matchTitle && !matchTactic) return false;
    }
    return true;
  });

  const byTactic: Record<string, TechniqueItem[]> = {};
  tacticOrder.forEach(tac => byTactic[tac] = []);
  filtered.forEach(t => {
    t.tactics.forEach(tac => {
      if (byTactic[tac] && !byTactic[tac].find(x => x.id === t.id)) {
        byTactic[tac].push(t);
      }
    });
  });

  const getVerdictBadgeStyle = (verdict: string) => {
    switch (verdict) {
      case 'PASS':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'TOO_NARROW':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'NOISY':
        return 'bg-slate-100 text-slate-700 border-slate-200';
      case 'SYNTAX_ERROR':
      case 'MISSED_SHOWN':
        return 'bg-rose-50 text-rose-700 border-rose-200';
      default:
        return 'bg-slate-50 text-slate-600 border-slate-200';
    }
  };

  const getRulePreview = (tech: TechniqueItem) => {
    const firstSet = tech.events ? Object.keys(tech.events)[0] : '1';
    const ev = tech.events ? tech.events[firstSet] : null;
    const proc = (ev && (ev as any).shown_image) || 'cmd.exe';
    const cmd = ev ? ev.shown : 'suspicious_command';
    const rawTitle = tech.title || tech.id;
    const cleanTitle = rawTitle.replace(/^Suspicious\s+/i, '');

    return `title: Suspicious ${cleanTitle}
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '${proc.replace(/^[a-zA-Z]:\\.*\\/, '\\')}'
        CommandLine|contains: '${(cmd || '').split(' ')[1] || 'exec'}'
    condition: selection
level: ${tech.best_verdict === 'PASS' ? 'high' : 'medium'}
tags:
    - attack.${(tech.tactics[0] || 'execution').toLowerCase().replace(' ', '_')}
    - attack.${tech.id.toLowerCase()}`;
  };

  const handleCopyRule = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedRule(true);
    setTimeout(() => setCopiedRule(false), 2000);
  };

  const passCount = techniques.filter(t => t.best_verdict === 'PASS').length;
  const narrowCount = techniques.filter(t => t.best_verdict === 'TOO_NARROW').length;

  return (
    <div className="w-full space-y-5">
      {/* 4 Summary Stat Ribbon (Fills top horizontally) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Techniques</div>
            <div className="text-2xl font-extrabold text-slate-900 font-mono mt-0.5">{techniques.length} Techniques</div>
            <div className="text-[11px] text-slate-500 mt-0.5">Across Sets 1, 2, and 3</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center font-bold text-xs">
            44
          </div>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Strict Verified</div>
            <div className="text-2xl font-extrabold text-slate-900 font-mono mt-0.5">{passCount} Passing</div>
            <div className="text-[11px] text-slate-500 mt-0.5">Zero evasion blindspots</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
            <CheckCircle2 className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Evasion Vulnerable</div>
            <div className="text-2xl font-extrabold text-slate-900 font-mono mt-0.5">{narrowCount} Too Narrow</div>
            <div className="text-[11px] text-slate-500 mt-0.5">Missed hidden attack variant</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center">
            <AlertTriangle className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Tactical Span</div>
            <div className="text-2xl font-extrabold text-slate-900 font-mono mt-0.5">14 / 14 Tactics</div>
            <div className="text-[11px] text-slate-500 mt-0.5">Sysmon Event 1 process telemetry</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center">
            <ShieldCheck className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Filter & Control Ribbon */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-4 w-full">
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-slate-500 text-[11px] uppercase tracking-wider">Test Set:</span>
            <select
              value={selectedSet}
              onChange={(e) => setSelectedSet(e.target.value)}
              className="bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1 text-xs text-slate-800 font-semibold focus:border-blue-500 focus:outline-none"
            >
              <option value="all">All Sets (44 techniques)</option>
              <option value="1">Set 1 - Development (12)</option>
              <option value="2">Set 2 - Baseline (12)</option>
              <option value="3">Set 3 - Final Test (20)</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="font-bold text-slate-500 text-[11px] uppercase tracking-wider">Verdict:</span>
            <select
              value={selectedVerdict}
              onChange={(e) => setSelectedVerdict(e.target.value)}
              className="bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1 text-xs text-slate-800 font-semibold focus:border-blue-500 focus:outline-none"
            >
              <option value="all">All Statuses ({techniques.length})</option>
              <option value="PASS">Passing Only ({passCount})</option>
              <option value="TOO_NARROW">Too Narrow Only ({narrowCount})</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 relative">
            <span className="font-bold text-slate-500 text-[11px] uppercase tracking-wider">Search:</span>
            <div className="relative">
              <Search className="w-3 h-3 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="ID, Title, or Tactic..."
                className="bg-slate-50 border border-slate-300 rounded-lg pl-7 pr-2.5 py-1 text-xs text-slate-800 focus:border-blue-500 focus:outline-none w-56"
              />
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-2 text-[10px] font-bold">
          <span className="px-2 py-0.5 rounded border bg-blue-50 text-blue-800 border-blue-200">PASS (Verified)</span>
          <span className="px-2 py-0.5 rounded border bg-amber-50 text-amber-800 border-amber-200">TOO_NARROW</span>
          <span className="px-2 py-0.5 rounded border bg-slate-100 text-slate-700 border-slate-200">NOISY</span>
          <span className="px-2 py-0.5 rounded border bg-slate-100 text-slate-600 border-slate-200">SYNTAX</span>
        </div>
      </div>

      {/* Main Split Matrix Workbench (Filling Height Properly) */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-5 items-stretch min-h-[580px] w-full">
        {/* Left Column: 14 Tactic Matrix Columns (8 Cols) */}
        <div className="xl:col-span-8 bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between overflow-hidden">
          <div>
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center justify-between border-b border-slate-100 pb-2">
              <span className="flex items-center gap-1.5 text-slate-700">
                <Filter className="w-3.5 h-3.5 text-blue-600" />
                <span>ATT&CK Enterprise Matrix Stages ({tacticOrder.length} Tactics)</span>
              </span>
              <span className="text-slate-500 font-sans font-medium text-[11px]">Select any tile to inspect live telemetry on the right &rarr;</span>
            </div>

            {/* Horizontal Scrollable Column Board with Vertical Scroll inside each column */}
            <div className="flex gap-3 overflow-x-auto pb-4 max-h-[540px] select-none">
              {tacticOrder.map((tac) => {
                const items = byTactic[tac] || [];
                const covered = items.filter(t => t.best_verdict === 'PASS').length;
                return (
                  <div key={tac} className="w-52 min-w-[13rem] flex flex-col bg-slate-50/80 border border-slate-200 rounded-lg p-2.5 shrink-0 max-h-[510px]">
                    {/* Tactic Column Header */}
                    <div className="pb-2 mb-2 border-b border-slate-200 flex flex-col justify-between min-h-[46px] shrink-0">
                      <div className="text-[11px] font-bold text-slate-800 leading-tight">{tac}</div>
                      <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1">
                        <span className="font-semibold text-slate-600">{items.length} tech</span>
                        <span className={`font-mono font-bold ${covered > 0 ? 'text-blue-700' : 'text-slate-400'}`}>
                          {covered}/{items.length}
                        </span>
                      </div>
                    </div>

                    {/* Column Technique Cards (Scrollable if many) */}
                    <div className="space-y-1.5 flex-1 overflow-y-auto pr-1">
                      {items.length === 0 ? (
                        <div className="py-6 text-center text-[10px] text-slate-400 italic">No techniques</div>
                      ) : (
                        items.sort((a, b) => a.id.localeCompare(b.id)).map((t) => {
                          const isSelected = selectedId === t.id;
                          return (
                            <div
                              key={t.id}
                              onClick={() => setSelectedId(t.id)}
                              className={`p-2.5 rounded-lg border text-left cursor-pointer transition-all bg-white hover:border-slate-400 hover:shadow-xs ${
                                isSelected ? 'ring-2 ring-blue-600 border-blue-600 bg-blue-50/20' : 'border-slate-200'
                              }`}
                            >
                              <div className="flex items-center justify-between text-[10px] font-mono font-bold">
                                <span className="text-slate-900">{t.id}</span>
                                <span className="text-[9px] font-sans px-1 rounded bg-slate-100 border border-slate-200 text-slate-600">
                                  S{t.sets.join(',')}
                                </span>
                              </div>
                              <div className="text-[10px] font-semibold text-slate-800 truncate mt-0.5" title={t.title}>
                                {t.title || 'Untitled'}
                              </div>
                              <div className="text-[9px] font-mono mt-1 text-slate-500 flex items-center justify-between">
                                <span className={`px-1.5 py-0.5 rounded text-[9px] font-sans font-bold border ${getVerdictBadgeStyle(t.best_verdict)}`}>
                                  {t.best_verdict}
                                </span>
                                <span className="text-blue-700 font-sans font-semibold">Inspect &rarr;</span>
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-mono">
            <span>Filtered Techniques: {filtered.length} / {techniques.length}</span>
            <span>Ground Truth: Sysmon 1 Process Creation</span>
          </div>
        </div>

        {/* Right Column: Live Technique & Sigma Rule Inspector (4 Cols) */}
        <div className="xl:col-span-4 bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between space-y-4">
          <div className="space-y-3.5">
            {/* Header */}
            <div className="border-b border-slate-100 pb-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold">Active Technique Inspector</span>
                <a
                  href={`https://attack.mitre.org/techniques/${selectedTech.id.replace('.', '/')}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[10px] font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
                >
                  <span>MITRE ATT&CK</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div className="flex items-baseline gap-2 mt-1">
                <h2 className="text-xl font-extrabold text-slate-900 font-mono">{selectedTech.id}</h2>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getVerdictBadgeStyle(selectedTech.best_verdict)}`}>
                  {selectedTech.best_verdict}
                </span>
              </div>
              <div className="text-xs font-semibold text-slate-700 mt-0.5">{selectedTech.title}</div>
            </div>

            {/* Tactical Meta */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <div className="text-[10px] font-bold text-slate-400 uppercase">Tactics</div>
                <div className="font-semibold text-slate-800 mt-0.5 truncate">{selectedTech.tactics.join(', ')}</div>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <div className="text-[10px] font-bold text-slate-400 uppercase">Telemetry Source</div>
                <div className="font-semibold text-slate-800 mt-0.5">Sysmon Event 1</div>
              </div>
            </div>

            {/* Ground Truth Test Events */}
            {selectedTech.events && Object.keys(selectedTech.events).length > 0 && (
              <div className="space-y-2 text-xs font-mono">
                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Ground Truth Test Telemetry:</div>
                {Object.entries(selectedTech.events).slice(0, 1).map(([setNum, ev]) => (
                  <div key={setNum} className="space-y-1.5">
                    <div className="p-2 rounded-lg bg-slate-50 border border-slate-200">
                      <div className="text-[9px] text-slate-500 font-bold uppercase mb-0.5 font-sans">Shown Attack Line:</div>
                      <div className="text-slate-800 break-all select-all font-semibold text-[11px] leading-tight">{ev.shown || 'N/A'}</div>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-50 border border-slate-200">
                      <div className="text-[9px] text-slate-500 font-bold uppercase mb-0.5 font-sans">Hidden Evasion Variant:</div>
                      <div className="text-slate-800 break-all select-all text-[11px] leading-tight">{ev.variant || 'N/A'}</div>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-50 border border-slate-200">
                      <div className="text-[9px] text-slate-500 font-bold uppercase mb-0.5 font-sans">Harmless Near-Miss Line:</div>
                      <div className="text-slate-800 break-all select-all text-[11px] leading-tight">{ev.benign || 'N/A'}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Generated Sigma Detection Rule Preview */}
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5 text-slate-700 font-bold text-[10px] uppercase tracking-wider">
                  <Terminal className="w-3.5 h-3.5 text-blue-600" />
                  <span>Sigma Rule Preview</span>
                </div>
                <button
                  onClick={() => handleCopyRule(getRulePreview(selectedTech))}
                  className="text-[10px] text-slate-500 hover:text-slate-800 flex items-center gap-1 cursor-pointer"
                >
                  {copiedRule ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                  <span>{copiedRule ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <pre className="bg-slate-950 p-3.5 rounded-lg text-slate-100 text-[11px] font-mono overflow-x-auto select-all leading-relaxed min-h-[280px]">
                {getRulePreview(selectedTech)}
              </pre>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center gap-2">
            <button
              onClick={() => onNavigateTab('gate')}
              className="flex-1 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Test in Gate Validator</span>
            </button>
            <button
              onClick={() => onNavigateTab('pipeline')}
              className="py-2 px-3 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold cursor-pointer"
            >
              Pipeline
            </button>
          </div>
        </div>
      </div>

      {/* Lower Section: Full Technique Telemetry Heatmap & Inventory Table (Completely Eliminates Empty Void) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden w-full">
        <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">Complete MITRE ATT&CK Technique Inventory ({filtered.length} Techniques)</h3>
            <p className="text-xs text-slate-500">Full telemetry mapping, test set assignment, and automated validation status</p>
          </div>
          <span className="text-xs text-slate-400 font-mono">Click any row to load into the Live Inspector above</span>
        </div>

        <div className="overflow-x-auto w-full">
          <table className="w-full text-xs text-left font-mono">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold font-sans">
                <th className="py-2.5 px-3">Technique ID</th>
                <th className="py-2.5 px-4 font-sans">Technique Title</th>
                <th className="py-2.5 px-3">Tactics</th>
                <th className="py-2.5 px-3">Set(s)</th>
                <th className="py-2.5 px-3">Ground Truth</th>
                <th className="py-2.5 px-3">Validation Verdict</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((t) => {
                const isSelected = selectedId === t.id;
                return (
                  <tr
                    key={t.id}
                    onClick={() => setSelectedId(t.id)}
                    className={`cursor-pointer transition-colors ${
                      isSelected ? 'bg-blue-50/40 font-semibold' : 'hover:bg-slate-50/80'
                    }`}
                  >
                    <td className="py-2.5 px-3 font-bold text-slate-900 font-mono">{t.id}</td>
                    <td className="py-2.5 px-4 text-slate-800 font-sans max-w-[280px] truncate" title={t.title}>
                      {t.title}
                    </td>
                    <td className="py-2.5 px-3 text-slate-600 font-sans">{t.tactics.join(', ')}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-700 text-[10px]">
                        Set {t.sets.join(', ')}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-500">Sysmon Event 1</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-sans font-bold border ${getVerdictBadgeStyle(t.best_verdict)}`}>
                        {t.best_verdict}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right font-sans">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedId(t.id);
                        }}
                        className="text-blue-700 hover:text-blue-900 font-semibold cursor-pointer"
                      >
                        Inspect &rarr;
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
