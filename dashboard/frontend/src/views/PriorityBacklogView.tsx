import { useState, useEffect, useMemo } from 'react';
import { Shield, AlertTriangle, CheckCircle2, Users, Search, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';

interface BacklogEntry {
  id: string;
  name: string;
  tactics: string[];
  url: string;
  group_count: number;
  top_groups: string[];
  in_pipeline: boolean;
  covered: boolean;
  set: number | null;
}

interface BacklogData {
  source: string;
  total_attack_techniques: number;
  total_groups: number;
  our_techniques: number;
  covered: number;
  backlog: BacklogEntry[];
}

type FilterMode = 'all' | 'uncovered' | 'in_pipeline';

export const PriorityBacklogView = () => {
  const [data, setData] = useState<BacklogData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterMode>('all');
  const [search, setSearch] = useState('');
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [sortField, setSortField] = useState<'group_count' | 'id' | 'name'>('group_count');
  const [sortAsc, setSortAsc] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch('/api/priority-backlog?limit=0')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(d => { setData(d); setLoading(false); })
      .catch(e => {
        setError(e.message || 'Failed to load priority backlog');
        setLoading(false);
      });
  }, []);

  const filtered = useMemo(() => {
    if (!data) return [];
    let rows = data.backlog;

    if (filter === 'uncovered') {
      rows = rows.filter(r => !r.covered);
    } else if (filter === 'in_pipeline') {
      rows = rows.filter(r => r.in_pipeline);
    }

    if (search.trim()) {
      const q = search.toLowerCase();
      rows = rows.filter(r =>
        r.id.toLowerCase().includes(q) ||
        r.name.toLowerCase().includes(q) ||
        r.tactics.some(t => t.toLowerCase().includes(q)) ||
        r.top_groups.some(g => g.toLowerCase().includes(q))
      );
    }

    const copy = [...rows];
    copy.sort((a, b) => {
      let cmp = 0;
      if (sortField === 'group_count') cmp = a.group_count - b.group_count;
      else if (sortField === 'id') cmp = a.id.localeCompare(b.id);
      else cmp = a.name.localeCompare(b.name);
      return sortAsc ? cmp : -cmp;
    });
    return copy;
  }, [data, filter, search, sortField, sortAsc]);

  const handleSort = (field: 'group_count' | 'id' | 'name') => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(field !== 'group_count');
    }
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (sortField !== field) return null;
    return sortAsc
      ? <ChevronUp className="w-3 h-3 inline ml-0.5" />
      : <ChevronDown className="w-3 h-3 inline ml-0.5" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-fg-muted text-sm">
        <div className="animate-pulse">Loading priority backlog...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-critical-muted border border-critical-edge rounded-lg p-4 text-critical text-sm">
        <AlertTriangle className="w-4 h-4 inline mr-2" />
        {error}
      </div>
    );
  }

  if (!data) return null;

  const uncoveredInPipeline = data.backlog.filter(r => r.in_pipeline && !r.covered).length;
  const maxGroupCount = Math.max(1, ...data.backlog.map(r => r.group_count));

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-panel p-3 rounded-lg border border-edge flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-fg flex items-center gap-2">
            <Shield className="w-4 h-4 text-brand" />
            Threat-Informed Priority Backlog
          </h2>
          <p className="text-[11px] text-fg-muted mt-0.5">
            Techniques ranked by how many active threat groups use them (MITRE ATT&CK via TAXII 2.1)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-[10px] px-2 py-0.5 rounded-md border font-medium ${
            data.source === 'taxii'
              ? 'text-pass bg-pass-muted border-pass-edge'
              : 'text-warn bg-warn-muted border-warn-edge'
          }`}>
            {data.source === 'taxii' ? 'TAXII Live' : 'Local Only'}
          </span>
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-panel rounded-lg border border-edge p-3">
          <div className="text-[10px] text-fg-muted uppercase tracking-wider">ATT&CK Techniques</div>
          <div className="text-xl font-bold text-fg mt-1">{data.total_attack_techniques}</div>
          <div className="text-[10px] text-fg-muted">full Enterprise catalog</div>
        </div>
        <div className="bg-panel rounded-lg border border-edge p-3">
          <div className="text-[10px] text-fg-muted uppercase tracking-wider">Threat Groups</div>
          <div className="text-xl font-bold text-fg mt-1">{data.total_groups}</div>
          <div className="text-[10px] text-fg-muted">active intrusion sets</div>
        </div>
        <div className="bg-panel rounded-lg border border-edge p-3">
          <div className="text-[10px] text-fg-muted uppercase tracking-wider">In Pipeline</div>
          <div className="text-xl font-bold text-fg mt-1">{data.our_techniques}</div>
          <div className="text-[10px] text-fg-muted">{data.covered} covered</div>
        </div>
        <div className="bg-panel rounded-lg border border-edge p-3">
          <div className="text-[10px] text-fg-muted uppercase tracking-wider">Uncovered Gap</div>
          <div className="text-xl font-bold text-critical mt-1">{uncoveredInPipeline}</div>
          <div className="text-[10px] text-fg-muted">in pipeline, no passing rule</div>
        </div>
      </div>

      {/* Filters and search */}
      <div className="bg-panel p-3 rounded-lg border border-edge flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1.5">
          {(['all', 'uncovered', 'in_pipeline'] as FilterMode[]).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors cursor-pointer ${
                filter === f
                  ? 'bg-brand text-brand-fg'
                  : 'bg-panel-inset text-fg-secondary hover:bg-panel-hover border border-edge'
              }`}
            >
              {f === 'all' ? 'All Techniques' : f === 'uncovered' ? 'Uncovered Only' : 'In Pipeline'}
            </button>
          ))}
        </div>
        <div className="flex-1 min-w-[200px] relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-fg-muted" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by ID, name, tactic or group..."
            className="w-full bg-panel-inset border border-edge rounded-md pl-8 pr-3 py-1.5 text-xs text-fg focus:border-brand focus:outline-none"
          />
        </div>
        <span className="text-[11px] text-fg-muted">{filtered.length} techniques</span>
      </div>

      {/* Table */}
      <div className="bg-panel rounded-lg border border-edge overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-panel-inset border-b border-edge text-fg-muted">
                <th className="px-3 py-2 text-left font-semibold w-8">#</th>
                <th
                  className="px-3 py-2 text-left font-semibold cursor-pointer select-none"
                  onClick={() => handleSort('id')}
                >
                  Technique <SortIcon field="id" />
                </th>
                <th
                  className="px-3 py-2 text-left font-semibold cursor-pointer select-none"
                  onClick={() => handleSort('name')}
                >
                  Name <SortIcon field="name" />
                </th>
                <th className="px-3 py-2 text-left font-semibold">Tactics</th>
                <th
                  className="px-3 py-2 text-center font-semibold cursor-pointer select-none"
                  onClick={() => handleSort('group_count')}
                >
                  Groups <SortIcon field="group_count" />
                </th>
                <th className="px-3 py-2 text-center font-semibold w-24">Threat Level</th>
                <th className="px-3 py-2 text-center font-semibold">Pipeline</th>
                <th className="px-3 py-2 text-center font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 200).map((row, idx) => {
                const isExpanded = expandedRow === row.id;
                const barWidth = Math.round((row.group_count / maxGroupCount) * 100);
                return (
                  <tr key={row.id} className="group">
                    <td className="px-3 py-2 text-fg-muted border-b border-subtle">{idx + 1}</td>
                    <td className="px-3 py-2 border-b border-subtle">
                      {row.url ? (
                        <a href={row.url} target="_blank" rel="noopener noreferrer"
                          className="font-mono font-semibold text-brand hover:underline inline-flex items-center gap-1">
                          {row.id}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <span className="font-mono font-semibold text-fg">{row.id}</span>
                      )}
                    </td>
                    <td className="px-3 py-2 border-b border-subtle text-fg-secondary max-w-[250px] truncate" title={row.name}>
                      {row.name}
                    </td>
                    <td className="px-3 py-2 border-b border-subtle">
                      <div className="flex flex-wrap gap-1">
                        {row.tactics.slice(0, 3).map(t => (
                          <span key={t} className="px-1.5 py-0.5 bg-panel-inset border border-edge rounded text-[10px] text-fg-muted">
                            {t}
                          </span>
                        ))}
                        {row.tactics.length > 3 && (
                          <span className="text-[10px] text-fg-muted">+{row.tactics.length - 3}</span>
                        )}
                      </div>
                    </td>
                    <td className="px-3 py-2 border-b border-subtle text-center">
                      <button
                        onClick={() => setExpandedRow(isExpanded ? null : row.id)}
                        className="cursor-pointer inline-flex items-center gap-1 text-fg font-semibold hover:text-brand"
                      >
                        <Users className="w-3 h-3 text-fg-muted" />
                        {row.group_count}
                      </button>
                    </td>
                    <td className="px-3 py-2 border-b border-subtle">
                      <div className="w-full bg-panel-inset rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            row.group_count > maxGroupCount * 0.6
                              ? 'bg-critical'
                              : row.group_count > maxGroupCount * 0.3
                                ? 'bg-warn'
                                : 'bg-pass'
                          }`}
                          style={{ width: `${barWidth}%` }}
                        />
                      </div>
                    </td>
                    <td className="px-3 py-2 border-b border-subtle text-center">
                      {row.in_pipeline ? (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-brand-muted text-brand border border-brand-edge font-medium">
                          Set {row.set}
                        </span>
                      ) : (
                        <span className="text-[10px] text-fg-muted">-</span>
                      )}
                    </td>
                    <td className="px-3 py-2 border-b border-subtle text-center">
                      {row.covered ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-pass">
                          <CheckCircle2 className="w-3 h-3" /> Covered
                        </span>
                      ) : row.in_pipeline ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-critical">
                          <AlertTriangle className="w-3 h-3" /> Gap
                        </span>
                      ) : (
                        <span className="text-[10px] text-fg-muted">Not in pipeline</span>
                      )}
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-3 py-8 text-center text-fg-muted">
                    No techniques match the current filter and search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        {filtered.length > 200 && (
          <div className="px-3 py-2 text-[11px] text-fg-muted border-t border-edge text-center">
            Showing first 200 of {filtered.length} techniques. Use search to narrow results.
          </div>
        )}
      </div>

      {/* Expanded group detail */}
      {expandedRow && (() => {
        const row = data.backlog.find(r => r.id === expandedRow);
        if (!row || row.top_groups.length === 0) return null;
        return (
          <div className="bg-panel rounded-lg border border-edge p-3">
            <div className="text-xs font-semibold text-fg mb-2">
              Groups using {row.id} ({row.group_count} total, showing up to 5):
            </div>
            <div className="flex flex-wrap gap-1.5">
              {row.top_groups.map(g => (
                <span key={g} className="px-2 py-1 bg-panel-inset border border-edge rounded-md text-[11px] text-fg-secondary font-medium">
                  {g}
                </span>
              ))}
              {row.group_count > 5 && (
                <span className="px-2 py-1 text-[11px] text-fg-muted">
                  and {row.group_count - 5} more
                </span>
              )}
            </div>
          </div>
        );
      })()}
    </div>
  );
};
