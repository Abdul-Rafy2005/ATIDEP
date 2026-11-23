import { Search, Cpu, GraduationCap } from 'lucide-react';

interface HeaderProps {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  activeTab: string;
}

export const Header = ({ searchQuery, setSearchQuery, activeTab }: HeaderProps) => {
  const tabTitles: Record<string, string> = {
    overview: 'Executive Security & Posture Overview',
    coverage: 'MITRE ATT&CK Matrix Navigator',
    runs: 'Empirical Evaluation Runs & Benchmarks',
    gate: 'Interactive Validation Gate Workbench',
    pipeline: 'CTI-to-Detection Pipeline Studio',
  };

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      {/* Title & Global Search */}
      <div className="flex items-center gap-6">
        <div>
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">ATIDEP Operations</div>
          <h1 className="text-sm font-extrabold text-slate-900 tracking-tight">{tabTitles[activeTab] || 'Platform Dashboard'}</h1>
        </div>

        <div className="hidden lg:flex items-center relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search threats, tactics, rules, runs..."
            className="bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-700 w-72 focus:bg-white focus:border-blue-500 focus:w-88 focus:outline-none transition-all"
          />
        </div>
      </div>

      {/* Telemetry Chips */}
      <div className="flex items-center gap-3 text-xs">
        <div className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200 text-slate-600 font-mono text-[11px]">
          <Cpu className="w-3.5 h-3.5 text-slate-400" />
          <span>RTX 4000 Ada (32GB)</span>
        </div>

        <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200 text-slate-700 font-mono text-[11px]">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Ollama: <strong className="text-slate-900 font-sans">qwen2.5-coder:14b</strong> (v3b)</span>
        </div>

        <div className="hidden sm:flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 font-mono text-[10px] font-bold border border-blue-200">
          <GraduationCap className="w-3.5 h-3.5 text-blue-600" />
          <span>FAST FYP-1</span>
        </div>
      </div>
    </header>
  );
};
