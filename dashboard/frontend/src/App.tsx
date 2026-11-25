import { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewView } from './views/OverviewView';
import { CoverageMatrixView } from './views/CoverageMatrixView';
import { RunsView } from './views/RunsView';
import { GateValidatorView } from './views/GateValidatorView';
import { PipelineView } from './views/PipelineView';
import { PriorityBacklogView } from './views/PriorityBacklogView';

const VALID_TABS = ['overview', 'coverage', 'runs', 'gate', 'pipeline', 'priority'] as const;

const getTabFromHash = (): string => {
  const hash = window.location.hash.replace(/^#\/?/, '').trim();
  return (VALID_TABS as readonly string[]).includes(hash) ? hash : 'overview';
};

function App() {
  const [activeTab, setActiveTab] = useState<string>(getTabFromHash);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedRunFolder, setSelectedRunFolder] = useState<string | null>(null);
  const [gateInitialData, setGateInitialData] = useState<{ techniqueId: string; set: number; ruleYaml: string } | null>(null);
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    try { return (localStorage.getItem('atidep-theme') as 'dark' | 'light') || 'dark'; }
    catch { return 'dark'; }
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.classList.toggle('dark', theme === 'dark');
    try { localStorage.setItem('atidep-theme', theme); } catch {}
  }, [theme]);

  useEffect(() => {
    const handlePopState = () => setActiveTab(getTabFromHash());
    window.addEventListener('popstate', handlePopState);
    window.addEventListener('hashchange', handlePopState);
    if (!window.location.hash) {
      window.history.replaceState({ tab: 'overview' }, '', '#/overview');
    }
    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('hashchange', handlePopState);
    };
  }, []);

  const navigateTab = useCallback((tab: string) => {
    setActiveTab(tab);
    const targetHash = `#/${tab}`;
    if (window.location.hash !== targetHash) {
      window.history.pushState({ tab }, '', targetHash);
    }
  }, []);

  const toggleTheme = useCallback(() => setTheme(t => t === 'dark' ? 'light' : 'dark'), []);

  return (
    <div className="flex h-screen w-full bg-background text-foreground font-sans antialiased overflow-hidden">
      <Sidebar activeTab={activeTab} setActiveTab={navigateTab} />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header searchQuery={searchQuery} setSearchQuery={setSearchQuery} activeTab={activeTab} theme={theme} onToggleTheme={toggleTheme} />
        <main className="flex-1 overflow-y-auto p-4 lg:p-6 w-full scroll-smooth">
          <div className="w-full max-w-[1600px]">
            {activeTab === 'overview' && <OverviewView onNavigateTab={navigateTab} onSelectRun={(folder) => setSelectedRunFolder(folder)} />}
            {activeTab === 'coverage' && <CoverageMatrixView onNavigateTab={navigateTab} onTestInGate={(data) => { setGateInitialData(data); navigateTab('gate'); }} searchFilter={searchQuery} />}
            {activeTab === 'runs' && <RunsView onNavigateTab={navigateTab} initialFolder={selectedRunFolder} searchFilter={searchQuery} />}
            {activeTab === 'gate' && <GateValidatorView initialData={gateInitialData} />}
            {activeTab === 'pipeline' && <PipelineView />}
            {activeTab === 'priority' && <PriorityBacklogView />}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
