import { useState, useEffect } from 'react';
import type { TechniqueItem } from '../types';
import { fallbackTechniques } from '../data/fallback';
import { ExternalLink, Play, Search, Copy, Check, Terminal } from 'lucide-react';
import { MetricCard } from '../components/ui/metric-card';
import { VerdictBadge } from '../components/ui/verdict-badge';

interface CoverageMatrixViewProps {
  onNavigateTab: (tab: string) => void;
  onTestInGate?: (data: { techniqueId: string; set: number; ruleYaml: string }) => void;
  searchFilter?: string;
}

const tacticOrder = [
  'Initial Access', 'Execution', 'Persistence', 'Privilege Escalation',
  'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
  'Collection', 'Command and Control', 'Exfiltration', 'Impact',
  'Resource Development', 'Reconnaissance'
];

export const CoverageMatrixView = ({ onNavigateTab, onTestInGate, searchFilter = '' }: CoverageMatrixViewProps) => {
  const [techniques, setTechniques] = useState<TechniqueItem[]>(fallbackTechniques);
  const [selectedSet, setSelectedSet] = useState<string>('all');
  const [selectedVerdict, setSelectedVerdict] = useState<string>('all');
  const [search, setSearch] = useState<string>(searchFilter);
  const [selectedId, setSelectedId] = useState<string>('T1059.001');
  const [copiedRule, setCopiedRule] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);

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
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const selectedTech = techniques.find(t => t.id === selectedId) || techniques[0] || fallbackTechniques[0];

  const filtered = techniques.filter(t => {
    if (selectedSet !== 'all' && !t.sets.includes(parseInt(selectedSet))) return false;
    if (selectedVerdict !== 'all' && t.best_verdict !== selectedVerdict) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      if (!t.id.toLowerCase().includes(q) && !(t.title || '').toLowerCase().includes(q) && !t.tactics.some(tac => tac.toLowerCase().includes(q))) return false;
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
    <div className="w-full space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 w-full">
        <MetricCard label="Total techniques" value={techniques.length} detail="Across sets 1, 2, and 3" className={loading ? 'animate-pulse' : ''} />
        <MetricCard label="Strict verified" value={`${passCount} passing`} detail="Zero evasion blindspots" className={loading ? 'animate-pulse' : ''} />
        <MetricCard label="Too narrow" value={narrowCount} detail="Missed hidden variant" className={loading ? 'animate-pulse' : ''} />
        <MetricCard label="Tactical span" value="14/14" detail="Sysmon Event 1 telemetry" />
      </div>

      {/* Filters */}
      <div className="bg-panel p-3 rounded-lg border border-edge flex flex-wrap items-center justify-between gap-3 w-full">
        <div className="flex flex-wrap items-center gap-2.5 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-fg-muted font-medium">Set:</span>
            <select value={selectedSet} onChange={(e) => setSelectedSet(e.target.value)}
              className="bg-panel-inset border border-edge rounded-md px-2 py-1 text-xs text-fg font-medium focus:border-brand focus:outline-none">
              <option value="all">All Sets (44)</option>
              <option value="1">Set 1 (12)</option>
              <option value="2">Set 2 (12)</option>
              <option value="3">Set 3 (20)</option>
            </select>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-fg-muted font-medium">Verdict:</span>
            <select value={selectedVerdict} onChange={(e) => setSelectedVerdict(e.target.value)}
              className="bg-panel-inset border border-edge rounded-md px-2 py-1 text-xs text-fg font-medium focus:border-brand focus:outline-none">
              <option value="all">All ({techniques.length})</option>
              <option value="PASS">Pass ({passCount})</option>
              <option value="TOO_NARROW">Too Narrow ({narrowCount})</option>
              <option value="NOISY">Noisy</option>
              <option value="SYNTAX_ERROR">Syntax Error</option>
            </select>
          </div>
          <div className="relative">
            <Search className="w-3 h-3 text-fg-muted absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
              placeholder="ID, title, or tactic..."
              className="bg-panel-inset border border-edge rounded-md pl-7 pr-2.5 py-1 text-xs text-fg focus:border-brand focus:outline-none w-48" />
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-semibold">
          <VerdictBadge verdict="PASS" />
          <VerdictBadge verdict="TOO_NARROW" />
          <VerdictBadge verdict="NOISY" />
          <VerdictBadge verdict="SYNTAX_ERROR" />
        </div>
      </div>

      {/* Matrix + Inspector */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-stretch min-h-[560px] w-full">
        <div className="xl:col-span-8 bg-panel p-3.5 rounded-lg border border-edge flex flex-col justify-between overflow-hidden">
          <div>
            <div className="text-[11px] text-fg-muted mb-2.5 flex items-center justify-between border-b border-subtle pb-2">
              <span className="font-medium text-fg-secondary">{tacticOrder.length} Tactics</span>
              <span>Select a tile to inspect</span>
            </div>

            <div className="flex gap-2.5 overflow-x-auto pb-3 max-h-[520px] select-none">
              {tacticOrder.map((tac) => {
                const items = byTactic[tac] || [];
                const covered = items.filter(t => t.best_verdict === 'PASS').length;
                return (
                  <div key={tac} className="w-48 min-w-[12rem] flex flex-col bg-panel-inset border border-edge rounded-md p-2 shrink-0 max-h-[490px]">
                    <div className="pb-1.5 mb-1.5 border-b border-subtle shrink-0">
                      <div className="text-[11px] font-semibold text-fg leading-tight">{tac}</div>
                      <div className="flex items-center justify-between text-[10px] text-fg-muted mt-0.5">
                        <span>{items.length} techniques</span>
                        <span className={`font-mono font-medium ${covered > 0 ? 'text-pass' : 'text-fg-muted'}`}>
                          {covered}/{items.length}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-1 flex-1 overflow-y-auto pr-1">
                      {items.length === 0 ? (
                        <div className="py-5 text-center text-[10px] text-fg-muted italic">No techniques</div>
                      ) : (
                        items.sort((a, b) => a.id.localeCompare(b.id)).map((t) => {
                          const isSelected = selectedId === t.id;
                          return (
                            <div key={t.id} onClick={() => setSelectedId(t.id)}
                              className={`p-2 rounded-md border text-left cursor-pointer transition-all bg-panel hover:border-edge-hover ${
                                isSelected ? 'ring-1 ring-brand border-brand' : 'border-edge'
                              }`}>
                              <div className="flex items-center justify-between text-[10px] font-mono font-medium">
                                <span className="text-fg">{t.id}</span>
                                <span className="text-[9px] px-1 rounded bg-panel-inset border border-edge text-fg-muted">
                                  S{t.sets.join(',')}
                                </span>
                              </div>
                              <div className="text-[10px] font-medium text-fg-secondary truncate mt-0.5" title={t.title}>
                                {t.title || 'Untitled'}
                              </div>
                              <div className="mt-1">
                                <VerdictBadge verdict={t.best_verdict} />
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

          <div className="pt-2 border-t border-subtle flex items-center justify-between text-[11px] text-fg-muted">
            <span>{filtered.length}/{techniques.length} techniques shown</span>
            <span className="font-mono">Sysmon Event 1</span>
          </div>
        </div>

        {/* Inspector */}
        <div className="xl:col-span-4 bg-panel p-4 rounded-lg border border-edge flex flex-col justify-between space-y-3">
          <div className="space-y-3">
            <div className="border-b border-subtle pb-2.5">
              <div className="flex items-center justify-between">
                <span className="text-[11px] text-fg-muted">Technique inspector</span>
                <a href={`https://attack.mitre.org/techniques/${selectedTech.id.replace('.', '/')}`}
                  target="_blank" rel="noreferrer"
                  className="text-[10px] font-medium text-brand hover:text-brand-hover flex items-center gap-1">
                  <span>MITRE ATT&CK</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div className="flex items-baseline gap-2 mt-1">
                <h2 className="text-lg font-bold text-fg font-mono">{selectedTech.id}</h2>
                <VerdictBadge verdict={selectedTech.best_verdict} />
              </div>
              <div className="text-xs text-fg-secondary mt-0.5">{selectedTech.title}</div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 bg-panel-inset rounded-md border border-edge">
                <div className="text-[10px] text-fg-muted">Tactics</div>
                <div className="font-medium text-fg mt-0.5 truncate">{selectedTech.tactics.join(', ')}</div>
              </div>
              <div className="p-2 bg-panel-inset rounded-md border border-edge">
                <div className="text-[10px] text-fg-muted">Telemetry</div>
                <div className="font-medium text-fg mt-0.5">Sysmon Event 1</div>
              </div>
            </div>

            {selectedTech.events && Object.keys(selectedTech.events).length > 0 && (
              <div className="space-y-1.5 text-xs font-mono">
                <div className="text-[11px] text-fg-muted font-sans">Ground truth test events</div>
                {Object.entries(selectedTech.events).slice(0, 1).map(([setNum, ev]) => (
                  <div key={setNum} className="space-y-1">
                    <div className="p-2 rounded-md bg-panel-inset border border-edge">
                      <div className="text-[10px] text-fg-muted font-sans mb-0.5">Shown attack</div>
                      <div className="text-fg-secondary break-all select-all text-[11px] leading-tight">{ev.shown || 'N/A'}</div>
                    </div>
                    <div className="p-2 rounded-md bg-panel-inset border border-edge">
                      <div className="text-[10px] text-fg-muted font-sans mb-0.5">Hidden variant</div>
                      <div className="text-fg-secondary break-all select-all text-[11px] leading-tight">{ev.variant || 'N/A'}</div>
                    </div>
                    <div className="p-2 rounded-md bg-panel-inset border border-edge">
                      <div className="text-[10px] text-fg-muted font-sans mb-0.5">Benign baseline</div>
                      <div className="text-fg-secondary break-all select-all text-[11px] leading-tight">{ev.benign || 'N/A'}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5 text-fg-secondary">
                  <Terminal className="w-3.5 h-3.5 text-brand" />
                  <span className="font-medium">Sigma rule preview</span>
                </div>
                <button onClick={() => handleCopyRule(getRulePreview(selectedTech))}
                  className="text-[10px] text-fg-muted hover:text-fg flex items-center gap-1 cursor-pointer">
                  {copiedRule ? <Check className="w-3 h-3 text-pass" /> : <Copy className="w-3 h-3" />}
                  <span>{copiedRule ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <pre className="bg-zinc-950 p-3 rounded-lg text-zinc-100 text-[11px] font-mono overflow-x-auto select-all leading-relaxed min-h-[260px] border border-zinc-800">
                {getRulePreview(selectedTech)}
              </pre>
            </div>
          </div>

          <div className="pt-2.5 border-t border-subtle flex items-center gap-2">
            <button
              onClick={() => {
                if (onTestInGate) {
                  onTestInGate({ techniqueId: selectedTech.id, set: selectedTech.sets[0] || 1, ruleYaml: getRulePreview(selectedTech) });
                } else {
                  onNavigateTab('gate');
                }
              }}
              className="flex-1 py-2 rounded-md bg-brand hover:bg-brand-hover text-brand-fg text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer">
              <Play className="w-3.5 h-3.5" />
              <span>Test in Gate</span>
            </button>
            <button onClick={() => onNavigateTab('pipeline')}
              className="py-2 px-3 rounded-md bg-panel-inset hover:bg-panel-hover border border-edge text-fg-secondary text-xs font-medium cursor-pointer">
              Pipeline
            </button>
          </div>
        </div>
      </div>

      {/* Full table */}
      <div className="bg-panel rounded-lg border border-edge overflow-hidden w-full">
        <div className="p-3.5 border-b border-subtle flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-fg">Technique Inventory ({filtered.length})</h3>
            <p className="text-[11px] text-fg-muted">Full telemetry mapping and validation status</p>
          </div>
        </div>

        <div className="overflow-x-auto w-full">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="bg-panel-inset border-b border-edge text-fg-muted font-medium">
                <th className="py-2 px-3">ID</th>
                <th className="py-2 px-4">Title</th>
                <th className="py-2 px-3">Tactics</th>
                <th className="py-2 px-3">Set(s)</th>
                <th className="py-2 px-3">Telemetry</th>
                <th className="py-2 px-3">Verdict</th>
                <th className="py-2 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-subtle">
              {filtered.map((t) => {
                const isSelected = selectedId === t.id;
                return (
                  <tr key={t.id} onClick={() => setSelectedId(t.id)}
                    className={`cursor-pointer transition-colors ${isSelected ? 'bg-brand-muted' : 'hover:bg-panel-hover'}`}>
                    <td className="py-2 px-3 font-mono font-medium text-fg">{t.id}</td>
                    <td className="py-2 px-4 text-fg-secondary max-w-[280px] truncate" title={t.title}>{t.title}</td>
                    <td className="py-2 px-3 text-fg-secondary">{t.tactics.join(', ')}</td>
                    <td className="py-2 px-3">
                      <span className="px-1.5 py-0.5 rounded bg-panel-inset border border-edge text-fg-muted text-[10px]">
                        Set {t.sets.join(', ')}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-fg-muted">Sysmon Event 1</td>
                    <td className="py-2 px-3"><VerdictBadge verdict={t.best_verdict} /></td>
                    <td className="py-2 px-3 text-right">
                      <button onClick={(e) => { e.stopPropagation(); setSelectedId(t.id); }}
                        className="text-brand hover:text-brand-hover font-medium cursor-pointer">
                        Inspect
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
