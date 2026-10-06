import React, { useState } from 'react';
import { Database, Cpu, Search, CheckCircle2 } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [llmProvider, setLlmProvider] = useState('mock');
  const [embeddingProvider, setEmbeddingProvider] = useState('mock');
  const [searchProvider, setSearchProvider] = useState('duckduckgo');

  return (
    <div className="space-y-6 py-4 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
          System Settings & Provider Configuration
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Configure API key environment parameters, embedding models, vector store settings, and reflection limits.
        </p>
      </div>

      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6 text-xs">
        {/* LLM Config */}
        <div>
          <h2 className="font-bold text-slate-900 text-sm mb-3 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-600" /> LLM Provider Engine
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { id: 'mock', name: 'Intelligent Mock Engine (Offline Demo)' },
              { id: 'openai', name: 'OpenAI (GPT-4o / GPT-4o-mini)' },
              { id: 'gemini', name: 'Google Gemini (Gemini 1.5 Flash)' }
            ].map((p) => (
              <button
                key={p.id}
                onClick={() => setLlmProvider(p.id)}
                className={`p-3 rounded-xl border text-left font-semibold transition-all ${
                  llmProvider === p.id
                    ? 'bg-blue-50 border-blue-500 text-blue-900 shadow-xs'
                    : 'bg-slate-50 border-slate-200 text-slate-700'
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* Embedding Config */}
        <div className="pt-4 border-t border-slate-100">
          <h2 className="font-bold text-slate-900 text-sm mb-3 flex items-center gap-2">
            <Database className="w-4 h-4 text-indigo-600" /> Vector Embedding Model
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { id: 'mock', name: 'Heuristic Vector Engine (384-dim)' },
              { id: 'openai', name: 'text-embedding-3-small' },
              { id: 'gemini', name: 'text-embedding-004' }
            ].map((p) => (
              <button
                key={p.id}
                onClick={() => setEmbeddingProvider(p.id)}
                className={`p-3 rounded-xl border text-left font-semibold transition-all ${
                  embeddingProvider === p.id
                    ? 'bg-indigo-50 border-indigo-500 text-indigo-900 shadow-xs'
                    : 'bg-slate-50 border-slate-200 text-slate-700'
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* Search Provider Config */}
        <div className="pt-4 border-t border-slate-100">
          <h2 className="font-bold text-slate-900 text-sm mb-3 flex items-center gap-2">
            <Search className="w-4 h-4 text-emerald-600" /> Web Search Provider
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { id: 'duckduckgo', name: 'DuckDuckGo Public Search (No API Key Required)' },
              { id: 'tavily', name: 'Tavily Research API' }
            ].map((p) => (
              <button
                key={p.id}
                onClick={() => setSearchProvider(p.id)}
                className={`p-3 rounded-xl border text-left font-semibold transition-all ${
                  searchProvider === p.id
                    ? 'bg-emerald-50 border-emerald-500 text-emerald-900 shadow-xs'
                    : 'bg-slate-50 border-slate-200 text-slate-700'
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* Database Status Monitor */}
        <div className="pt-4 border-t border-slate-100 bg-slate-50 p-4 rounded-xl space-y-2">
          <p className="font-bold text-slate-900 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Database & Vector Store Status
          </p>
          <p className="text-slate-600">
            Engine: <strong>PostgreSQL + pgvector</strong> (SQLite fallback active for local offline execution).
          </p>
        </div>
      </div>
    </div>
  );
};
