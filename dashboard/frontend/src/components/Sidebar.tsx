import {
  LayoutDashboard,
  Grid3X3,
  ListFilter,
  CheckCircle2,
  Workflow,
} from 'lucide-react';
import { AtidepLogo } from './AtidepLogo';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar = ({ activeTab, setActiveTab }: SidebarProps) => {
  const navItems = [
    {
      group: 'Analysis',
      items: [
        { id: 'overview', label: 'Overview', icon: LayoutDashboard },
        { id: 'coverage', label: 'ATT&CK Coverage', icon: Grid3X3 },
        { id: 'runs', label: 'Evaluation Runs', icon: ListFilter },
      ]
    },
    {
      group: 'Engineering',
      items: [
        { id: 'gate', label: 'Gate Validator', icon: CheckCircle2 },
        { id: 'pipeline', label: 'Pipeline Studio', icon: Workflow },
      ]
    }
  ];

  return (
    <aside className="w-52 bg-zinc-950 text-zinc-400 border-r border-zinc-800/50 flex flex-col justify-between select-none shrink-0 h-screen sticky top-0">
      <div className="p-3 space-y-5 overflow-y-auto">
        <div className="flex items-center gap-2.5 px-2 py-1">
          <AtidepLogo className="w-6 h-6 shrink-0 text-cyan-400" size={24} />
          <div>
            <span className="font-semibold text-zinc-100 text-[13px] tracking-tight">ATIDEP</span>
            <div className="text-[9px] text-zinc-600">Detection Engineering</div>
          </div>
        </div>

        <div className="space-y-4">
          {navItems.map((section, idx) => (
            <div key={idx} className="space-y-0.5">
              <div className="text-[10px] font-medium text-zinc-600 px-3 mb-1">{section.group}</div>
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center gap-2.5 px-3 py-1.5 rounded-md text-[12px] font-medium transition-colors cursor-pointer focus:outline-none focus-visible:ring-1 focus-visible:ring-cyan-400/50 ${
                      isActive
                        ? 'bg-cyan-400/10 text-cyan-400'
                        : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.04]'
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-zinc-600'}`} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      <div className="p-3 border-t border-zinc-800/50">
        <div className="flex items-center gap-2 px-1">
          <div className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 text-[10px] font-bold flex items-center justify-center">AR</div>
          <div className="overflow-hidden">
            <div className="text-[11px] font-medium text-zinc-300 truncate">Abdul Rafy</div>
            <div className="text-[9px] text-zinc-600 truncate">FAST-NUCES</div>
          </div>
        </div>
      </div>
    </aside>
  );
};
