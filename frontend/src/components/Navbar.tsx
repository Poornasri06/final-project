import React from 'react';
import { ShieldCheck, Activity, Menu, Sparkles } from 'lucide-react';

interface NavbarProps {
  onToggleSidebar: () => void;
  onNavigate: (page: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar, onNavigate }) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-30 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="md:hidden p-2 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <Menu className="w-6 h-6" />
          </button>
          
          <div 
            onClick={() => onNavigate('landing')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-teal-500 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/25 group-hover:scale-105 transition-all">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-white group-hover:text-blue-400 transition-colors">E.V.I.D.A.</span>
                <span className="px-2.5 py-0.5 text-[11px] font-bold bg-teal-500/10 text-teal-400 border border-teal-500/30 rounded-full flex items-center gap-1.5 uppercase tracking-wide">
                  <Activity className="w-3 h-3 text-teal-400" /> Healthcare
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block font-medium">Evidence Verification & Intelligent Domain Analysis System</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">

          
          <button
            onClick={() => onNavigate('new-research')}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-sm px-4 py-2 rounded-xl transition-all shadow-md shadow-blue-500/20 flex items-center gap-2 active:scale-95"
          >
            <Sparkles className="w-4 h-4 text-blue-200" /> Start Research
          </button>
        </div>
      </div>
    </header>
  );
};
