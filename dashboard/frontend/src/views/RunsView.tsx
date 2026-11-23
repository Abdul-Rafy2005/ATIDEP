import { useState, useEffect } from 'react';
import type { RunItem } from '../types';
import { fallbackRuns } from '../data/fallback';
import { Search, CheckCircle2, Trophy, Cpu, Play, Filter, ShieldAlert } from 'lucide-react';

interface RunsViewProps {
  onNavigateTab: (tab: string) => void;
  searchFilter?: string;
}

export const RunsView = ({ onNavigateTab, searchFilter = '' }: RunsViewProps) => {
  const [runs, setRuns] = useState<RunItem[]>(fallbackRuns);
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [setFilter, setSetFilter] = useState<string>('all');
  const [search, setSearch] = useState<string>(searchFilter);
  const [selectedFolder, setSelectedFolder] = useState<string>(fallbackRuns[0]?.folder || '20261111_1500_set3_v3b');

  useEffect(() => {
    fetch('/api/runs')
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data && data.length) {
          const sorted = (data as RunItem[]).slice().sort((a, b) => b.folder.localeCompare(a.folder));
          setRuns(sorted);
          if (!sorted.some(r => r.folder === selectedFolder)) {
            setSelectedFolder(sorted[0].folder);
          }
        }
      })
      .catch(() => {});
  }, []);

  const filtered = runs.filter(r => {
    if (roleFilter !== 'all' && r.label !== roleFilter) return false;
    if (setFilter !== 'all' && r.set.toString() !== setFilter) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      const matchFolder = r.folder.toLowerCase().includes(q);
      const matchPrompt = (r.prompt || '').toLowerCase().includes(q);
      const matchModel = r.models.join(' ').toLowerCase().includes(q);
      if (!matchFolder && !matchPrompt && !matchModel) return false;
    }
    return true;
  });

  const selectedRun = runs.find(r => r.folder === selectedFolder) || filtered[0] || runs[0];

  const getRoleBadgeStyle = (label: string) => {
    switch (label) {
      case 'primary':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'baseline':
        return 'bg-slate-100 text-slate-800 border-slate-200';
      case 'exploratory':
        return 'bg-slate-100 text-slate-700 border-slate-200';
      default:
        return 'bg-slate-50 text-slate-600 border-slate-200';
    }
  };

  const selStrictPct = selectedRun ? Math.round((100 * selectedRun.strict_pass) / (selectedRun.total || 1)) : 0;
  const selSinglePct = selectedRun ? Math.round((100 * selectedRun.single_pass) / (selectedRun.total || 1)) : 0;
  const selSyntaxPct = selectedRun ? Math.round((100 * (selectedRun.total - selectedRun.syntax_errors)) / (selectedRun.total || 1)) : 0;

  return (
    <div className="w-full space-y-5">
      {/* 4 Summary Stat Ribbon */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Evaluation Batches</div>
            <div className="text-2xl font-extrabold text-slate-900 font-mono mt-0.5">{runs.length} Runs</div>
            <div className="text-[11px] text-slate-500 mt-0.5">Across Sets 1, 2, and 3</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center font-bold text-xs">
            14
          </div>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Scored Sigma Rules</div>
            <div className="text-2xl font-extrabold text-slate-900 font-mono mt-0.5">804 Rules</div>
            <div className="text-[11px] text-slate-500 mt-0.5">Empirically gate scored</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center">
            <CheckCircle2 className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Primary Winner</div>
            <div className="text-xl font-extrabold text-blue-700 font-mono mt-0.5 truncate">14b (v3b)</div>
            <div className="text-[11px] text-slate-500 mt-0.5">57/60 Strict Pass (95.0%)</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
            <Trophy className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Local Testbed</div>
            <div className="text-xl font-extrabold text-slate-900 font-mono mt-0.5">RTX 4000 Ada</div>
            <div className="text-[11px] text-slate-500 mt-0.5">100% Offline Ollama Inference</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center">
            <Cpu className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Main Split Workbench (Runs Table Left 8 Cols, Deep-Dive Inspector Right 4 Cols) */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-5 items-stretch min-h-[580px] w-full">
        {/* Left: Interactive Evaluation Batches Table (8 Cols) */}
        <div className="xl:col-span-8 bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between overflow-hidden">
          <div>
            {/* Filter Toolbar */}
            <div className="pb-3 mb-3 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-3 text-xs">
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-slate-500 text-[11px] uppercase tracking-wider">Role:</span>
                  <select
                    value={roleFilter}
                    onChange={(e) => setRoleFilter(e.target.value)}
                    className="bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1 text-xs text-slate-800 font-semibold focus:border-blue-500 focus:outline-none"
                  >
                    <option value="all">All Roles ({runs.length})</option>
                    <option value="primary">Primary (Frozen Winner)</option>
                    <option value="baseline">Baseline (Comparison)</option>
                    <option value="exploratory">Exploratory</option>
                    <option value="development">Development</option>
                  </select>
                </div>

                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-slate-500 text-[11px] uppercase tracking-wider">Set:</span>
                  <select
                    value={setFilter}
                    onChange={(e) => setSetFilter(e.target.value)}
                    className="bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1 text-xs text-slate-800 font-semibold focus:border-blue-500 focus:outline-none"
                  >
                    <option value="all">All Sets</option>
                    <option value="1">Set 1 (Development)</option>
                    <option value="3">Set 3 (Final Locked Test)</option>
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
                      placeholder="Folder, prompt, or model..."
                      className="bg-slate-50 border border-slate-300 rounded-lg pl-7 pr-2.5 py-1 text-xs text-slate-800 focus:border-blue-500 focus:outline-none w-52"
                    />
                  </div>
                </div>
              </div>

              <div className="text-[11px] font-mono text-slate-500">
                Showing <strong className="text-slate-900">{filtered.length}</strong> / {runs.length} batches
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto w-full max-h-[500px] overflow-y-auto">
              <table className="w-full text-xs text-left font-mono">
                <thead className="sticky top-0 bg-slate-50 z-10">
                  <tr className="border-b border-slate-200 text-slate-600 font-semibold font-sans">
                    <th className="py-2.5 px-3">Run Folder</th>
                    <th className="py-2.5 px-2.5">Date</th>
                    <th className="py-2.5 px-2.5">Set</th>
                    <th className="py-2.5 px-2.5">Prompt</th>
                    <th className="py-2.5 px-3">Model</th>
                    <th className="py-2.5 px-3">Strict Pass</th>
                    <th className="py-2.5 px-2.5">Single</th>
                    <th className="py-2.5 px-2.5">Syntax</th>
                    <th className="py-2.5 px-2.5">Role</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filtered.map((r) => {
                    const isSelected = selectedRun && selectedRun.folder === r.folder;
                    const pct = Math.round((100 * r.strict_pass) / (r.total || 1));
                    return (
                      <tr
                        key={r.folder}
                        onClick={() => setSelectedFolder(r.folder)}
                        className={`cursor-pointer transition-colors ${
                          isSelected ? 'bg-blue-50/50 font-semibold' : 'hover:bg-slate-50/80'
                        }`}
                      >
                        <td className="py-2.5 px-3 font-bold text-slate-900 font-mono text-[11px]">{r.folder}</td>
                        <td className="py-2.5 px-2.5 text-slate-500 font-sans text-[11px]">
                          {r.date ? r.date.split('T')[0] : 'N/A'}
                        </td>
                        <td className="py-2.5 px-2.5 font-bold text-slate-800">Set {r.set}</td>
                        <td className="py-2.5 px-2.5 text-blue-700 font-bold">{r.prompt}</td>
                        <td className="py-2.5 px-3 text-slate-700 truncate max-w-[120px]" title={r.models.join(', ')}>
                          {r.models.map(m => m.replace('qwen2.5-coder:', '')).join(', ')}
                        </td>
                        <td className="py-2.5 px-3 font-bold text-slate-900 font-mono">
                          <div className="flex items-center gap-1.5">
                            <span className="text-blue-700">{r.strict_pass}/{r.total}</span>
                            <span className="text-[10px] text-slate-400 font-normal">({pct}%)</span>
                          </div>
                        </td>
                        <td className="py-2.5 px-2.5 text-blue-600">{r.single_pass}/{r.total}</td>
                        <td className={`py-2.5 px-2.5 ${r.syntax_errors > 0 ? 'text-red-600 font-bold' : 'text-slate-400'}`}>
                          {r.syntax_errors}
                        </td>
                        <td className="py-2.5 px-2.5">
                          <span className={`px-1.5 py-0.5 rounded text-[9px] font-sans uppercase font-bold border ${getRoleBadgeStyle(r.label)}`}>
                            {r.label}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-right font-sans">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedFolder(r.folder);
                            }}
                            className="text-blue-700 hover:text-blue-900 font-semibold cursor-pointer text-[11px]"
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

          <div className="pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-mono">
            <span>Storage: results/runs/</span>
            <span>Gate Standard: Catch Shown + Catch Hidden Variant</span>
          </div>
        </div>

        {/* Right: Live Batch Deep-Dive Inspector (4 Cols) */}
        {selectedRun && (
          <div className="xl:col-span-4 bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between space-y-4">
            <div className="space-y-4">
              {/* Header */}
              <div className="border-b border-slate-100 pb-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold">Batch Telemetry Inspector</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${getRoleBadgeStyle(selectedRun.label)}`}>
                    {selectedRun.label}
                  </span>
                </div>
                <h2 className="text-lg font-extrabold text-slate-900 font-mono mt-1 break-all">{selectedRun.folder}</h2>
                <div className="text-xs text-slate-500 font-sans mt-0.5">
                  Executed on {selectedRun.date ? selectedRun.date.replace('T', ' ') : 'N/A'}
                </div>
              </div>

              {/* Architecture & Run Parameters */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-[10px] font-bold text-slate-400 uppercase">Model Architecture</div>
                  <div className="font-semibold text-slate-800 mt-0.5 truncate" title={selectedRun.models.join(', ')}>
                    {selectedRun.models.join(', ')}
                  </div>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-[10px] font-bold text-slate-400 uppercase">Prompt Revision</div>
                  <div className="font-bold text-blue-700 mt-0.5">Prompt {selectedRun.prompt}</div>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-[10px] font-bold text-slate-400 uppercase">Test Corpus</div>
                  <div className="font-semibold text-slate-800 mt-0.5">
                    Set {selectedRun.set} {selectedRun.set === 3 ? '(Locked Test)' : '(Development)'}
                  </div>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="text-[10px] font-bold text-slate-400 uppercase">Inference Config</div>
                  <div className="font-semibold text-slate-800 mt-0.5 font-mono">
                    T={selectedRun.temperature} | Rep={selectedRun.repeats}
                  </div>
                </div>
              </div>

              {/* Gate Metrics Visual Progress Meters */}
              <div className="space-y-3">
                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Gate Verification Progress</div>

                <div className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700">Strict Pass (Caught + Variant)</span>
                    <span className="font-mono text-blue-700">{selectedRun.strict_pass} / {selectedRun.total} ({selStrictPct}%)</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div className="bg-blue-600 h-2 rounded-full transition-all duration-300" style={{ width: `${selStrictPct}%` }}></div>
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700">Single Pass (Shown Line Recall)</span>
                    <span className="font-mono text-blue-700">{selectedRun.single_pass} / {selectedRun.total} ({selSinglePct}%)</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div className="bg-blue-500 h-2 rounded-full transition-all duration-300" style={{ width: `${selSinglePct}%` }}></div>
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-700">Syntax Integrity</span>
                    <span className="font-mono text-slate-700">
                      {selectedRun.total - selectedRun.syntax_errors} / {selectedRun.total} ({selSyntaxPct}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${selectedRun.syntax_errors > 0 ? 'bg-amber-500' : 'bg-slate-700'}`}
                      style={{ width: `${selSyntaxPct}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Error Breakdown Diagnostic Cards */}
              <div className="space-y-2">
                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Failure Mode Attribution</div>
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2 rounded-lg bg-amber-50/70 border border-amber-200">
                    <div className="text-[10px] text-amber-800 font-sans font-bold">Too Narrow (Variant Miss)</div>
                    <div className="text-base font-extrabold text-amber-900 mt-0.5">{selectedRun.too_narrow}</div>
                  </div>
                  <div className="p-2 rounded-lg bg-red-50/70 border border-red-200">
                    <div className="text-[10px] text-red-800 font-sans font-bold">Syntax Failures</div>
                    <div className="text-base font-extrabold text-red-900 mt-0.5">{selectedRun.syntax_errors}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Actions */}
            <div className="pt-3 border-t border-slate-100 flex items-center gap-2">
              <button
                onClick={() => onNavigateTab('matrix')}
                className="flex-1 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Filter className="w-3.5 h-3.5" />
                <span>ATT&CK Matrix View</span>
              </button>
              <button
                onClick={() => onNavigateTab('gate')}
                className="py-2 px-3 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1 cursor-pointer"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Gate Tester</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Lower Analytics & Protocol Deck (Fills entire lower screen) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 w-full">
        {/* Card 1: Set 3 Final Locked Test Tournament */}
        <div className="bg-white p-4.5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between space-y-3">
          <div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center gap-1.5">
                <Trophy className="w-4 h-4 text-blue-600" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Set 3 Final Benchmark Tournament</h3>
              </div>
              <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                20 Fresh Techniques
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">Evaluated across 3 repeats (60 trials each) with zero data contamination.</p>

            <div className="space-y-2 mt-3 text-xs">
              <div>
                <div className="flex justify-between text-[11px] font-semibold mb-0.5">
                  <span className="text-slate-800 font-bold">qwen2.5-coder:14b (v3b) [Primary Winner]</span>
                  <span className="font-mono font-bold text-blue-700">57 / 60 (95.0%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '95%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] font-semibold mb-0.5">
                  <span className="text-slate-700">qwen2.5-coder:7b (v3a) [Comparison]</span>
                  <span className="font-mono font-bold text-blue-600">54 / 60 (90.0%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: '90%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] font-semibold mb-0.5">
                  <span className="text-slate-600">qwen2.5-coder:14b (v3a) [Exploratory]</span>
                  <span className="font-mono text-slate-600">55 / 60 (91.7%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className="bg-slate-400 h-2 rounded-full" style={{ width: '91.7%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] font-semibold mb-0.5">
                  <span className="text-slate-600">Prompt v1 Baseline (14b & 7b)</span>
                  <span className="font-mono text-slate-600">83 / 120 (69.2%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className="bg-slate-300 h-2 rounded-full" style={{ width: '69.2%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-500">
            Winner Decision: 14b under v3b achieved highest generalization with 0 syntax failures.
          </div>
        </div>

        {/* Card 2: Prompt Engineering Trajectory */}
        <div className="bg-white p-4.5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between space-y-3">
          <div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-blue-600" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Prompt Evolution Trajectory</h3>
              </div>
              <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                Set 1 Strict Pass
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">Iterative refinement of SigmaHQ syntax constraints and generalization cues.</p>

            <div className="space-y-2 mt-3 text-xs">
              <div className="p-2 rounded bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-800">Prompt v1 (Initial Baseline)</div>
                  <div className="text-[10px] text-slate-500">Copy-the-line overfit vulnerability</div>
                </div>
                <span className="font-mono font-bold text-slate-700">27.8%</span>
              </div>

              <div className="p-2 rounded bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-800">Prompt v2 (Syntax Guidance)</div>
                  <div className="text-[10px] text-slate-500">Windash nested mapping issue</div>
                </div>
                <span className="font-mono font-bold text-slate-700">72.2%</span>
              </div>

              <div className="p-2 rounded bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-800">Prompt v2.1 & v3b (Final Optimization)</div>
                  <div className="text-[10px] text-slate-500">Clean list format, zero syntax defects</div>
                </div>
                <span className="font-mono font-bold text-blue-700">95.0% (Set 3)</span>
              </div>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-500">
            Guidance frozen in llm/prompts/v3b.py for reproducibility.
          </div>
        </div>

        {/* Card 3: Research Rigor & Testbed Specifications */}
        <div className="bg-white p-4.5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between space-y-3">
          <div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4 text-slate-700" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Empirical Research Rigor</h3>
              </div>
              <span className="text-[10px] font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                FYP-1 Protocol
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">Pre-registered evaluation controls to guarantee scientific validity.</p>

            <div className="space-y-2 mt-3 text-xs text-slate-600">
              <div className="p-2 rounded bg-slate-50 border border-slate-200">
                <div className="font-bold text-slate-800 mb-0.5">Strict Gate Anti-Cheat</div>
                <p className="text-[11px]">Rules copying the observed command line fail the strict gate with <code className="text-amber-800 font-bold">TOO_NARROW</code>.</p>
              </div>

              <div className="p-2 rounded bg-slate-50 border border-slate-200">
                <div className="font-bold text-slate-800 mb-0.5">100% Offline Local Inference</div>
                <p className="text-[11px]">Dell Precision 3680 (i7-14700, 32GB RAM, RTX 4000 Ada 20GB). No cloud API calls.</p>
              </div>

              <div className="p-2 rounded bg-slate-50 border border-slate-200">
                <div className="font-bold text-slate-800 mb-0.5">Clean Set 3 Test Partition</div>
                <p className="text-[11px]">Set 3 was built and locked before testing; prompts were never tuned against it.</p>
              </div>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-500">
            Supervised by Dr. Shahbaz Siddiqui, FAST-NUCES.
          </div>
        </div>
      </div>
    </div>
  );
};
