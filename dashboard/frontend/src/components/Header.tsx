import { Search, Sun, Moon } from 'lucide-react';

interface HeaderProps {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  activeTab: string;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

export const Header = ({ searchQuery, setSearchQuery, activeTab, theme, onToggleTheme }: HeaderProps) => {
  const tabTitles: Record<string, string> = {
    overview: 'Overview',
    coverage: 'ATT&CK Coverage Matrix',
    runs: 'Evaluation Runs',
    gate: 'Gate Validator',
    pipeline: 'Pipeline Studio',
  };

  return (
    <header className="bg-panel border-b border-edge px-5 py-2.5 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-5">
        <h1 className="text-sm font-semibold text-fg tracking-tight">{tabTitles[activeTab] || 'Dashboard'}</h1>
        <div className="hidden lg:flex items-center relative">
          <Search className="w-3.5 h-3.5 text-fg-muted absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search techniques, rules, runs..."
            className="bg-panel-inset border border-edge rounded-lg pl-9 pr-3 py-1.5 text-xs text-fg w-60 focus:border-brand focus:outline-none focus-visible:ring-1 focus-visible:ring-brand/40 transition-colors placeholder:text-fg-muted"
          />
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        <button
          onClick={onToggleTheme}
          className="p-1.5 rounded-lg text-fg-muted hover:text-fg hover:bg-panel-hover transition-colors cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/40"
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-panel-inset border border-edge text-fg-secondary text-[11px]">
          <span className="relative flex h-2 w-2"><span className="absolute inline-flex h-full w-full rounded-full bg-pass opacity-75 animate-ping"></span><span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-pass"></span></span>
          <span>Ollama</span>
          <span className="font-medium text-fg font-mono text-[10px]">14b</span>
        </div>
      </div>
    </header>
  );
};
