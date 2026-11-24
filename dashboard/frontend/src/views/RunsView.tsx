import { useState, useEffect } from 'react';
import type { RunItem } from '../types';
import { fallbackRuns } from '../data/fallback';
import { Search, Play, Filter, ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';
import { MetricCard } from '../components/ui/metric-card';
import { getRoleBadgeStyle } from '../components/ui/verdict-badge';

interface RunsViewProps {
  onNavigateTab: (tab: string) => void;
  initialFolder?: string | null;
  searchFilter?: string;
}

type SortKey = 'folder' | 'set' | 'prompt' | 'strict' | 'single' | 'errors' | 'label';

const SortIcon = ({ active, dir }: { active: boolean; dir: 'asc' | 'desc' }) => {
  if (!active) return <ChevronsUpDown className="w-3 h-3 text-fg-muted opacity-0 group-hover:opacity-60 inline ml-0.5" />;
  return dir === 'asc'
    ? <ChevronUp className="w-3 h-3 text-brand inline ml-0.5" />
    : <ChevronDown className="w-3 h-3 text-brand inline ml-0.5" />;
};

export const RunsView = ({ onNavigateTab, initialFolder, searchFilter = '' }: RunsViewProps) => {
  const [runs, setRuns] = useState<RunItem[]>(fallbackRuns);
  const [loading, setLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [setFilter, setSetFilter] = useState<string>('all');
  const [search, setSearch] = useState<string>(searchFilter);
  const [selectedFolder, setSelectedFolder] = useState<string>(initialFolder || fallbackRuns[0]?.folder || '20261111_1500_set3_v3b');
  const [sortKey, setSortKey] = useState<SortKey>('folder');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    if (initialFolder) setSelectedFolder(initialFolder);
  }, [initialFolder]);

  useEffect(() => {
    fetch('/api/runs')
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data && data.length) {
          const sorted = (data as RunItem[]).slice().sort((a, b) => b.folder.localeCompare(a.folder));
          setRuns(sorted);
          if (initialFolder) {
            setSelectedFolder(initialFolder);
          } else if (!sorted.some(r => r.folder === selectedFolder)) {
            setSelectedFolder(sorted[0].folder);
          }
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  const filtered = runs.filter(r => {
    if (roleFilter !== 'all' && r.label !== roleFilter) return false;
    if (setFilter !== 'all' && r.set.toString() !== setFilter) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      if (!r.folder.toLowerCase().includes(q) && !(r.prompt || '').toLowerCase().includes(q) && !r.models.join(' ').toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const sorted = [...filtered].sort((a, b) => {
    const dir = sortDir === 'asc' ? 1 : -1;
    switch (sortKey) {
      case 'folder': return a.folder.localeCompare(b.folder) * dir;
      case 'set': return (a.set - b.set) * dir;
      case 'prompt': return a.prompt.localeCompare(b.prompt) * dir;
      case 'strict': return (a.strict_pass - b.strict_pass) * dir;
      case 'single': return (a.single_pass - b.single_pass) * dir;
      case 'errors': return (a.syntax_errors - b.syntax_errors) * dir;
      case 'label': return a.label.localeCompare(b.label) * dir;
      default: return 0;
    }
  });

  const selectedRun = runs.find(r => r.folder === selectedFolder) || filtered[0] || runs[0];

  const totalRules = runs.reduce((sum, r) => sum + r.total, 0);
  const primaryRun = runs.find(r => r.label === 'primary');
  const primaryLabel = primaryRun ? primaryRun.models[0]?.replace('qwen2.5-coder:', '') + ' (' + primaryRun.prompt + ')' : '14b (v3b)';

  const selStrictPct = selectedRun ? Math.round((100 * selectedRun.strict_pass) / (selectedRun.total || 1)) : 0;
  const selSinglePct = selectedRun ? Math.round((100 * selectedRun.single_pass) / (selectedRun.total || 1)) : 0;
  const selSyntaxPct = selectedRun ? Math.round((100 * (selectedRun.total - selectedRun.syntax_errors)) / (selectedRun.total || 1)) : 0;

  return (
    <div className="w-full space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 w-full">
        <MetricCard label="Evaluation batches" value={`${runs.length} runs`} detail="Across sets 1, 2, and 3" className={loading ? 'animate-pulse' : ''} />
        <MetricCard label="Rules scored" value={totalRules} detail="Empirically gate verified" className={loading ? 'animate-pulse' : ''} />
        <MetricCard label="Primary winner" value={primaryLabel} detail={primaryRun ? `${primaryRun.strict_pass}/${primaryRun.total} strict pass` : ''} />
        <MetricCard label="Inference" value="Ollama" detail="100% offline local" />
      </div>

      {/* Table + Inspector */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-stretch min-h-[560px] w-full">
        <div className="xl:col-span-8 bg-panel p-3.5 rounded-lg border border-edge flex flex-col justify-between overflow-hidden">
          <div>
            <div className="pb-2.5 mb-2.5 border-b border-subtle flex flex-wrap items-center justify-between gap-2.5">
              <div className="flex flex-wrap items-center gap-2.5 text-xs">
                <div className="flex items-center gap-1.5">
                  <span className="text-fg-muted font-medium">Role:</span>
                  <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}
                    className="bg-panel-inset border border-edge rounded-md px-2 py-1 text-xs text-fg font-medium focus:border-brand focus:outline-none">
                    <option value="all">All ({runs.length})</option>
                    <option value="primary">Primary</option>
                    <option value="baseline">Baseline</option>
                    <option value="exploratory">Exploratory</option>
                    <option value="development">Development</option>
                  </select>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-fg-muted font-medium">Set:</span>
                  <select value={setFilter} onChange={(e) => setSetFilter(e.target.value)}
                    className="bg-panel-inset border border-edge rounded-md px-2 py-1 text-xs text-fg font-medium focus:border-brand focus:outline-none">
                    <option value="all">All Sets</option>
                    <option value="1">Set 1</option>
                    <option value="3">Set 3</option>
                  </select>
                </div>
                <div className="relative">
                  <Search className="w-3 h-3 text-fg-muted absolute left-2.5 top-1/2 -translate-y-1/2" />
                  <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
                    placeholder="Folder, prompt, model..."
                    className="bg-panel-inset border border-edge rounded-md pl-7 pr-2.5 py-1 text-xs text-fg focus:border-brand focus:outline-none w-44" />
                </div>
              </div>
              <div className="text-[11px] text-fg-muted">{filtered.length}/{runs.length} shown</div>
            </div>

            <div className="overflow-x-auto w-full max-h-[480px] overflow-y-auto">
              <table className="w-full text-xs text-left">
                <thead className="sticky top-0 bg-panel-inset z-10">
                  <tr className="border-b border-edge text-fg-muted font-medium">
                    <th className="py-2 px-2.5 cursor-pointer group select-none" onClick={() => handleSort('folder')}>
                      Run <SortIcon active={sortKey === 'folder'} dir={sortDir} />
                    </th>
                    <th className="py-2 px-2">Date</th>
                    <th className="py-2 px-2 cursor-pointer group select-none" onClick={() => handleSort('set')}>
                      Set <SortIcon active={sortKey === 'set'} dir={sortDir} />
                    </th>
                    <th className="py-2 px-2 cursor-pointer group select-none" onClick={() => handleSort('prompt')}>
                      Prompt <SortIcon active={sortKey === 'prompt'} dir={sortDir} />
                    </th>
                    <th className="py-2 px-2.5">Model</th>
                    <th className="py-2 px-2.5 cursor-pointer group select-none" onClick={() => handleSort('strict')}>
                      Strict <SortIcon active={sortKey === 'strict'} dir={sortDir} />
                    </th>
                    <th className="py-2 px-2 cursor-pointer group select-none" onClick={() => handleSort('single')}>
                      Single <SortIcon active={sortKey === 'single'} dir={sortDir} />
                    </th>
                    <th className="py-2 px-2 cursor-pointer group select-none" onClick={() => handleSort('errors')}>
                      Errors <SortIcon active={sortKey === 'errors'} dir={sortDir} />
                    </th>
                    <th className="py-2 px-2 cursor-pointer group select-none" onClick={() => handleSort('label')}>
                      Role <SortIcon active={sortKey === 'label'} dir={sortDir} />
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-subtle">
                  {sorted.map((r) => {
                    const isSelected = selectedRun && selectedRun.folder === r.folder;
                    const pct = Math.round((100 * r.strict_pass) / (r.total || 1));
                    return (
                      <tr key={r.folder} onClick={() => setSelectedFolder(r.folder)}
                        className={`cursor-pointer transition-colors ${isSelected ? 'bg-brand-muted' : 'hover:bg-panel-hover'}`}>
                        <td className="py-2 px-2.5 font-mono font-medium text-fg text-[11px]">{r.folder}</td>
                        <td className="py-2 px-2 text-fg-muted text-[11px]">{r.date ? r.date.split('T')[0] : 'N/A'}</td>
                        <td className="py-2 px-2 font-medium text-fg">Set {r.set}</td>
                        <td className="py-2 px-2 text-brand font-medium">{r.prompt}</td>
                        <td className="py-2 px-2.5 text-fg-secondary truncate max-w-[110px]" title={r.models.join(', ')}>
                          {r.models.map(m => m.replace('qwen2.5-coder:', '')).join(', ')}
                        </td>
                        <td className="py-2 px-2.5 font-mono font-medium text-fg">
                          <span className="text-brand">{r.strict_pass}/{r.total}</span>
                          <span className="text-fg-muted text-[10px] ml-1">({pct}%)</span>
                        </td>
                        <td className="py-2 px-2 text-fg-secondary font-mono">{r.single_pass}/{r.total}</td>
                        <td className={`py-2 px-2 font-mono ${r.syntax_errors > 0 ? 'text-critical font-semibold' : 'text-fg-muted'}`}>
                          {r.syntax_errors}
                        </td>
                        <td className="py-2 px-2">
                          <span className={`px-1.5 py-0.5 rounded text-[9px] font-semibold border ${getRoleBadgeStyle(r.label)}`}>
                            {r.label}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="pt-2 border-t border-subtle flex items-center justify-between text-[11px] text-fg-muted">
            <span>Storage: results/runs/</span>
            <span>Gate: shown + variant + quiet</span>
          </div>
        </div>

        {/* Inspector */}
        {selectedRun && (
          <div className="xl:col-span-4 bg-panel p-4 rounded-lg border border-edge flex flex-col justify-between space-y-3">
            <div className="space-y-3">
              <div className="border-b border-subtle pb-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-fg-muted">Run inspector</span>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${getRoleBadgeStyle(selectedRun.label)}`}>
                    {selectedRun.label}
                  </span>
                </div>
                <h2 className="text-base font-bold text-fg font-mono mt-1 break-all">{selectedRun.folder}</h2>
                <div className="text-xs text-fg-muted mt-0.5">
                  {selectedRun.date ? selectedRun.date.replace('T', ' ') : 'N/A'}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 bg-panel-inset rounded-md border border-edge">
                  <div className="text-[10px] text-fg-muted">Model</div>
                  <div className="font-medium text-fg mt-0.5 truncate" title={selectedRun.models.join(', ')}>
                    {selectedRun.models.join(', ')}
                  </div>
                </div>
                <div className="p-2 bg-panel-inset rounded-md border border-edge">
                  <div className="text-[10px] text-fg-muted">Prompt</div>
                  <div className="font-medium text-brand mt-0.5">{selectedRun.prompt}</div>
                </div>
                <div className="p-2 bg-panel-inset rounded-md border border-edge">
                  <div className="text-[10px] text-fg-muted">Test set</div>
                  <div className="font-medium text-fg mt-0.5">
                    Set {selectedRun.set} {selectedRun.set === 3 ? '(Locked)' : '(Dev)'}
                  </div>
                </div>
                <div className="p-2 bg-panel-inset rounded-md border border-edge">
                  <div className="text-[10px] text-fg-muted">Config</div>
                  <div className="font-medium text-fg mt-0.5 font-mono">
                    T={selectedRun.temperature} R={selectedRun.repeats}
                  </div>
                </div>
              </div>

              <div className="space-y-2.5">
                <div className="text-xs font-medium text-fg-secondary">Gate verification</div>
                {[
                  { label: 'Strict pass', value: selectedRun.strict_pass, total: selectedRun.total, pct: selStrictPct, barClass: 'bg-brand' },
                  { label: 'Single pass', value: selectedRun.single_pass, total: selectedRun.total, pct: selSinglePct, barClass: 'bg-brand opacity-60' },
                  { label: 'Syntax OK', value: selectedRun.total - selectedRun.syntax_errors, total: selectedRun.total, pct: selSyntaxPct, barClass: selectedRun.syntax_errors > 0 ? 'bg-narrow' : 'bg-fg-muted' },
                ].map((m) => (
                  <div key={m.label} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-fg-secondary">{m.label}</span>
                      <span className="font-mono font-medium text-fg">{m.value}/{m.total} ({m.pct}%)</span>
                    </div>
                    <div className="w-full bg-panel-inset rounded-full h-1.5 overflow-hidden">
                      <div className={`${m.barClass} h-1.5 rounded-full transition-all duration-300`} style={{ width: `${m.pct}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 rounded-md bg-narrow-muted border border-narrow-edge">
                  <div className="text-narrow font-medium">Too narrow</div>
                  <div className="text-lg font-bold text-narrow mt-0.5">{selectedRun.too_narrow}</div>
                </div>
                <div className="p-2 rounded-md bg-critical-muted border border-critical-edge">
                  <div className="text-critical font-medium">Syntax errors</div>
                  <div className="text-lg font-bold text-critical mt-0.5">{selectedRun.syntax_errors}</div>
                </div>
              </div>
            </div>

            <div className="pt-2.5 border-t border-subtle flex items-center gap-2">
              <button onClick={() => onNavigateTab('coverage')}
                className="flex-1 py-2 rounded-md bg-brand hover:bg-brand-hover text-brand-fg text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer">
                <Filter className="w-3.5 h-3.5" />
                <span>ATT&CK Matrix</span>
              </button>
              <button onClick={() => onNavigateTab('gate')}
                className="py-2 px-3 rounded-md bg-panel-inset hover:bg-panel-hover border border-edge text-fg-secondary text-xs font-medium flex items-center gap-1 cursor-pointer">
                <Play className="w-3.5 h-3.5" />
                <span>Gate</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Analytics cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 w-full">
        <div className="bg-panel p-3.5 rounded-lg border border-edge space-y-2.5">
          <div className="pb-2 border-b border-subtle">
            <h3 className="text-xs font-semibold text-fg">Set 3 Benchmark</h3>
            <p className="text-[11px] text-fg-muted mt-0.5">3 repeats, 60 trials each, zero contamination</p>
          </div>
          <div className="space-y-2 text-xs">
            {[
              { label: '14b (v3b) Primary', score: '57/60 (95.0%)', pct: 95, barClass: 'bg-brand' },
              { label: '7b (v3a) Comparison', score: '58/60 (96.7%)', pct: 96.7, barClass: 'bg-brand opacity-60' },
              { label: '14b (v3a) Exploratory', score: '55/60 (91.7%)', pct: 91.7, barClass: 'bg-fg-muted' },
              { label: 'v1 Baseline', score: '82/120 (68.3%)', pct: 68.3, barClass: 'bg-edge-hover' },
            ].map((m) => (
              <div key={m.label}>
                <div className="flex justify-between text-[11px] mb-0.5">
                  <span className="text-fg-secondary">{m.label}</span>
                  <span className="font-mono font-medium text-fg">{m.score}</span>
                </div>
                <div className="w-full bg-panel-inset rounded-full h-1.5">
                  <div className={`${m.barClass} h-1.5 rounded-full`} style={{ width: `${m.pct}%` }}></div>
                </div>
              </div>
            ))}
          </div>
          <div className="pt-2 border-t border-subtle text-[11px] text-fg-muted">
            Winner: 14b (v3b) with zero syntax failures.
          </div>
        </div>

        <div className="bg-panel p-3.5 rounded-lg border border-edge space-y-2.5">
          <div className="pb-2 border-b border-subtle">
            <h3 className="text-xs font-semibold text-fg">Prompt Evolution</h3>
            <p className="text-[11px] text-fg-muted mt-0.5">Iterative refinement of Sigma syntax constraints</p>
          </div>
          <div className="space-y-1.5 text-xs">
            {[
              { version: 'v1 (Initial)', issue: 'Copy-the-line overfit', score: '27.8%' },
              { version: 'v2 (Syntax guidance)', issue: 'Windash mapping issue', score: '72.2%' },
              { version: 'v3b (Final)', issue: 'Clean format, zero defects', score: '95.0% (Set 3)' },
            ].map((p) => (
              <div key={p.version} className="p-2 rounded-md bg-panel-inset border border-edge flex items-center justify-between">
                <div>
                  <div className="font-medium text-fg">{p.version}</div>
                  <div className="text-[10px] text-fg-muted">{p.issue}</div>
                </div>
                <span className="font-mono font-medium text-fg-secondary">{p.score}</span>
              </div>
            ))}
          </div>
          <div className="pt-2 border-t border-subtle text-[11px] text-fg-muted">
            Frozen in llm/prompts/v3b.py for reproducibility.
          </div>
        </div>

        <div className="bg-panel p-3.5 rounded-lg border border-edge space-y-2.5">
          <div className="pb-2 border-b border-subtle">
            <h3 className="text-xs font-semibold text-fg">Research Protocol</h3>
            <p className="text-[11px] text-fg-muted mt-0.5">Pre-registered evaluation controls</p>
          </div>
          <div className="space-y-1.5 text-xs text-fg-secondary">
            <div className="p-2 rounded-md bg-panel-inset border border-edge">
              <div className="font-medium text-fg mb-0.5">Strict gate anti-cheat</div>
              <p className="text-[11px]">Rules copying observed command fail with TOO_NARROW.</p>
            </div>
            <div className="p-2 rounded-md bg-panel-inset border border-edge">
              <div className="font-medium text-fg mb-0.5">100% offline inference</div>
              <p className="text-[11px]">Dell Precision 3680, RTX 4000 Ada 20GB. Zero cloud calls.</p>
            </div>
            <div className="p-2 rounded-md bg-panel-inset border border-edge">
              <div className="font-medium text-fg mb-0.5">Clean Set 3 partition</div>
              <p className="text-[11px]">Built and locked before testing. No prompt tuning on it.</p>
            </div>
          </div>
          <div className="pt-2 border-t border-subtle text-[11px] text-fg-muted">
            Supervised by Dr. Shahbaz Siddiqui, FAST-NUCES.
          </div>
        </div>
      </div>
    </div>
  );
};
