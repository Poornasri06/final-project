import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { ResearchSession, KnowledgeBaseStats } from '../types';
import { PlusCircle, ChevronRight } from 'lucide-react';

interface DashboardPageProps {
  onNavigate: (page: string) => void;
  onSelectSession: (sessionId: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate, onSelectSession }) => {
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [kbStats, setKbStats] = useState<KnowledgeBaseStats | null>(null);

  useEffect(() => {
    api.getResearchSessions().then(setSessions).catch(console.error);
    api.getKnowledgeBaseStats().then(setKbStats).catch(console.error);
  }, []);

  const totalClaims = sessions.reduce((acc, s) => acc + (s.claims_count || 0), 0);
  const totalSources = sessions.reduce((acc, s) => acc + (s.sources_count || 0), 0);

  return (
    <div className="space-y-6 py-4">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-blue-950 text-white p-6 rounded-2xl shadow-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">Domain Research Hub</span>
          <h1 className="text-2xl font-black mt-1">Healthcare Research Evidence Platform</h1>
          <p className="text-xs text-slate-300 mt-1 max-w-xl">
            Traceable claim verification engine backed by structure-aware pgvector document chunks and multi-agent audit pipeline.
          </p>
        </div>

        <button
          onClick={() => onNavigate('new-research')}
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl text-xs transition-all shadow-lg flex items-center gap-2 shrink-0"
        >
          <PlusCircle className="w-4 h-4" /> Start New Research
        </button>
      </div>

      {/* Metrics Cards Grid coming from PostgreSQL */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Research Sessions</p>
          <p className="text-3xl font-black text-slate-900 mt-1">{sessions.length}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Indexed Documents</p>
          <p className="text-3xl font-black text-blue-600 mt-1">{kbStats?.indexed_count ?? 4}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Extracted Claims</p>
          <p className="text-3xl font-black text-emerald-600 mt-1">{totalClaims}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Evaluated Sources</p>
          <p className="text-3xl font-black text-indigo-600 mt-1">{totalSources}</p>
        </div>
      </div>

      {/* Recent Research Sessions Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Recent Research Sessions</h2>
            <p className="text-xs text-slate-500 mt-0.5">Database history of evidence verification runs.</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-100/70 border-b border-slate-200 text-xs font-bold text-slate-600 uppercase tracking-wider">
                <th className="py-3.5 px-4">Research Topic</th>
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4">Claims</th>
                <th className="py-3.5 px-4">Sources</th>
                <th className="py-3.5 px-4">Conflicts</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-sm">
              {sessions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 text-xs">
                    No research sessions found. Click "Start New Research" to begin.
                  </td>
                </tr>
              ) : (
                sessions.map((s) => (
                  <tr
                    key={s.id}
                    onClick={() => onSelectSession(s.id)}
                    className="hover:bg-blue-50/50 cursor-pointer transition-colors group"
                  >
                    <td className="py-4 px-4 max-w-xs font-semibold text-slate-900 truncate">
                      {s.question}
                    </td>
                    <td className="py-4 px-4 text-xs text-slate-500">{s.created_at}</td>
                    <td className="py-4 px-4 font-bold text-slate-800">{s.claims_count}</td>
                    <td className="py-4 px-4 font-bold text-slate-800">{s.sources_count}</td>
                    <td className="py-4 px-4 text-xs font-semibold text-amber-700">{s.conflicts_count}</td>
                    <td className="py-4 px-4">
                      <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        {s.status}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <div className="inline-flex items-center gap-1 text-blue-600 group-hover:text-blue-700 text-xs font-semibold">
                        View Report <ChevronRight className="w-4 h-4" />
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
