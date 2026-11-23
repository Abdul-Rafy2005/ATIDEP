import { 
  LayoutDashboard, 
  Grid3X3, 
  ListFilter, 
  CheckCircle2, 
  Workflow, 
  ShieldCheck
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar = ({ activeTab, setActiveTab }: SidebarProps) => {
  const navItems = [
    {
      group: 'Operations & Intelligence',
      items: [
        { id: 'overview', label: 'Executive Overview', icon: LayoutDashboard },
        { id: 'coverage', label: 'ATT&CK Matrix', icon: Grid3X3 },
        { id: 'runs', label: 'Evaluation Runs', icon: ListFilter },
      ]
    },
    {
      group: 'Validation & Engineering',
      items: [
        { id: 'gate', label: 'Gate Validator', icon: CheckCircle2 },
        { id: 'pipeline', label: 'Pipeline Studio', icon: Workflow },
      ]
    }
  ];

  return (
    <aside className="w-64 bg-slate-950 text-slate-300 border-r border-slate-800/80 flex flex-col justify-between select-none shrink-0 h-screen sticky top-0">
      <div className="p-4 space-y-6 overflow-y-auto">
        {/* Brand emblem */}
        <div className="flex items-center gap-3 px-2 py-1">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center font-extrabold text-white text-sm shadow-md shadow-blue-500/20">
            A
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-white text-base tracking-tight">ATIDEP</span>
              <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                PROTOTYPE
              </span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono">SOC Sentinel v3.4</div>
          </div>
        </div>

        {/* Navigation Sections */}
        <div className="space-y-6">
          {navItems.map((section, idx) => (
            <div key={idx} className="space-y-1.5">
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-1">
                {section.group}
              </div>
              <div className="space-y-1">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                        isActive
                          ? 'bg-blue-600 text-white font-semibold shadow-sm shadow-blue-600/30'
                          : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/60'
                      }`}
                    >
                      <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-slate-900 bg-slate-950/60 space-y-3">
        <div className="flex items-center justify-between text-xs px-1">
          <div className="flex items-center gap-2 text-slate-400 font-mono text-[11px]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>SYSTEM HEALTHY</span>
          </div>
          <span className="text-emerald-400 font-mono text-[11px] font-bold">99.98%</span>
        </div>

        <div className="flex items-center gap-2.5 pt-2 border-t border-slate-900 px-1">
          <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-500 text-white text-xs font-bold flex items-center justify-center shadow-inner">
            AR
          </div>
          <div className="overflow-hidden">
            <div className="text-xs font-semibold text-slate-200 truncate flex items-center gap-1">
              <span>Abdul Rafy</span>
              <ShieldCheck className="w-3 h-3 text-blue-400 inline" />
            </div>
            <div className="text-[10px] text-slate-400 truncate">Lead Detection Engineer</div>
          </div>
        </div>
      </div>
    </aside>
  );
};
