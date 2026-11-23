import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewView } from './views/OverviewView';
import { CoverageMatrixView } from './views/CoverageMatrixView';
import { RunsView } from './views/RunsView';
import { GateValidatorView } from './views/GateValidatorView';
import { PipelineView } from './views/PipelineView';

function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [searchQuery, setSearchQuery] = useState<string>('');

  return (
    <div className="flex h-screen w-full bg-slate-50 text-slate-900 font-sans antialiased overflow-hidden">
      {/* Deep Dark Navy Enterprise Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main App Layout */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header Bar */}
        <Header searchQuery={searchQuery} setSearchQuery={setSearchQuery} activeTab={activeTab} />

        {/* Scrollable Viewport (full-width, tight elegant margins) */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6 w-full">
          <div className="w-full">
            {activeTab === 'overview' && <OverviewView onNavigateTab={setActiveTab} />}
            {activeTab === 'coverage' && <CoverageMatrixView onNavigateTab={setActiveTab} searchFilter={searchQuery} />}
            {activeTab === 'runs' && <RunsView onNavigateTab={setActiveTab} searchFilter={searchQuery} />}
            {activeTab === 'gate' && <GateValidatorView />}
            {activeTab === 'pipeline' && <PipelineView />}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
