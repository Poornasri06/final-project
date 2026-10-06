import {
  LayoutDashboard, PlusCircle, Database, Table,
  Layers, BarChart3, Settings, BookOpen
} from 'lucide-react';

interface SidebarProps {
  activePage: string;
  onNavigate: (page: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activePage, onNavigate, isOpen, onClose }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'new-research', label: 'New Research', icon: PlusCircle },
    { id: 'knowledge-base', label: 'Healthcare Knowledge Base', icon: Database },
    { id: 'evidence-matrix', label: 'Evidence Matrix', icon: Table },
    { id: 'rag-explainability', label: 'RAG Explainability', icon: Layers },
    { id: 'evaluation', label: 'Benchmark Evaluation', icon: BarChart3 },
    { id: 'settings', label: 'System Settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-slate-900/40 z-40 md:hidden backdrop-blur-xs"
        />
      )}

      <aside
        className={`fixed md:sticky top-16 left-0 z-40 w-64 h-[calc(100vh-4rem)] bg-white border-r border-slate-200/80 transition-transform duration-200 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="p-4 flex flex-col justify-between h-full overflow-y-auto">
          <div className="space-y-1.5">
            <div className="px-3 py-2 text-[11px] font-bold text-slate-400 uppercase tracking-widest">
              Research Platform
            </div>

            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onNavigate(item.id);
                    onClose();
                  }}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150 ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20 translate-x-0.5'
                      : 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900'
                  }`}
                >
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span className="truncate">{item.label}</span>
                </button>
              );
            })}
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100">
            <div className="bg-gradient-to-br from-slate-900 to-slate-800 p-3.5 rounded-xl text-xs text-white shadow-md">
              <p className="font-bold flex items-center gap-1.5 text-blue-300">
                <BookOpen className="w-4 h-4 text-blue-400" /> Evidence Pipeline Active
              </p>
              <p className="text-slate-300 text-[11px] mt-1.5 leading-relaxed">
                Claims cross-verified against indexed medical literature and pgvector embeddings.
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
