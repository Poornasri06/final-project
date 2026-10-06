import React, { useState } from 'react';
import { Sparkles, Filter, Database, Globe, Brain, HelpCircle } from 'lucide-react';

interface NewResearchPageProps {
  onStartResearch: (params: any) => void;
}

export const NewResearchPage: React.FC<NewResearchPageProps> = ({ onStartResearch }) => {
  const [question, setQuestion] = useState('What are the major risk factors associated with Type 2 diabetes?');
  const [domain, setDomain] = useState('Healthcare');
  const [depth, setDepth] = useState('Standard');
  const [useKb, setUseKb] = useState(true);
  const [useWeb, setUseWeb] = useState(true);
  const [useMemory, setUseMemory] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState('All');

  const exampleQuestions = [
    "What are the major risk factors associated with Type 2 diabetes?",
    "What evidence exists regarding lifestyle interventions for hypertension?",
    "What are the commonly reported complications of diabetes?",
    "What factors are associated with cardiovascular disease?",
    "What evidence supports early screening for hypertension?"
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    onStartResearch({
      question,
      domain,
      research_depth: depth,
      use_knowledge_base: useKb,
      use_web_search: useWeb,
      use_memory: useMemory,
      category_filter: categoryFilter === 'All' ? undefined : categoryFilter
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-4">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900">Initiate New Research Session</h1>
        <p className="text-xs text-slate-500 mt-1">
          Enter your healthcare question to execute the 14-step evidence verification pipeline.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-6">
        {/* Question Text Area */}
        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
            Research Question
          </label>
          <textarea
            rows={4}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. What are the major risk factors associated with Type 2 diabetes?"
            className="w-full p-4 border border-slate-300 rounded-xl text-sm font-medium text-slate-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            required
          />
        </div>

        {/* Quick Example Templates */}
        <div>
          <p className="text-xs font-semibold text-slate-500 mb-2 flex items-center gap-1">
            <HelpCircle className="w-3.5 h-3.5 text-blue-600" /> Example Healthcare Questions:
          </p>
          <div className="flex flex-wrap gap-2">
            {exampleQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setQuestion(q)}
                className="text-xs bg-slate-100 hover:bg-blue-50 hover:text-blue-700 text-slate-700 px-3 py-1.5 rounded-lg border border-slate-200 transition-colors text-left"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Grid Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 border-t border-slate-100">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Demonstration Domain
            </label>
            <select
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-lg text-sm text-slate-800 font-medium"
            >
              <option value="Healthcare">Healthcare Research</option>
              <option value="General">Other Configured Domain</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Research Depth
            </label>
            <div className="grid grid-cols-3 gap-2">
              {['Quick', 'Standard', 'Deep'].map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDepth(d)}
                  className={`py-2 text-xs font-semibold rounded-lg border transition-all ${
                    depth === d
                      ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Source Checkboxes */}
        <div className="pt-2 border-t border-slate-100">
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
            Search Sources & Memory
          </label>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <label className={`p-3 rounded-xl border flex items-center gap-3 cursor-pointer transition-all ${useKb ? 'bg-blue-50/60 border-blue-300' : 'bg-slate-50 border-slate-200'}`}>
              <input
                type="checkbox"
                checked={useKb}
                onChange={(e) => setUseKb(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <div className="text-xs">
                <p className="font-bold text-slate-900 flex items-center gap-1">
                  <Database className="w-3.5 h-3.5 text-blue-600" /> Knowledge Base
                </p>
                <p className="text-slate-500">pgvector Chunks</p>
              </div>
            </label>

            <label className={`p-3 rounded-xl border flex items-center gap-3 cursor-pointer transition-all ${useWeb ? 'bg-blue-50/60 border-blue-300' : 'bg-slate-50 border-slate-200'}`}>
              <input
                type="checkbox"
                checked={useWeb}
                onChange={(e) => setUseWeb(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <div className="text-xs">
                <p className="font-bold text-slate-900 flex items-center gap-1">
                  <Globe className="w-3.5 h-3.5 text-blue-600" /> Web Research
                </p>
                <p className="text-slate-500">Tavily / DDG APIs</p>
              </div>
            </label>

            <label className={`p-3 rounded-xl border flex items-center gap-3 cursor-pointer transition-all ${useMemory ? 'bg-blue-50/60 border-blue-300' : 'bg-slate-50 border-slate-200'}`}>
              <input
                type="checkbox"
                checked={useMemory}
                onChange={(e) => setUseMemory(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <div className="text-xs">
                <p className="font-bold text-slate-900 flex items-center gap-1">
                  <Brain className="w-3.5 h-3.5 text-blue-600" /> Prior Memory
                </p>
                <p className="text-slate-500">Session Memory</p>
              </div>
            </label>
          </div>
        </div>

        {/* Category Filter Dropdown */}
        <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-semibold text-slate-700">Category Filter:</span>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="p-1.5 bg-slate-50 border border-slate-300 rounded text-xs text-slate-800"
            >
              <option value="All">All Categories</option>
              <option value="Diabetes">Diabetes</option>
              <option value="Cardiovascular Disease">Cardiovascular Disease</option>
              <option value="Hypertension">Hypertension</option>
              <option value="General Healthcare">General Healthcare</option>
            </select>
          </div>

          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-md transition-all flex items-center gap-2 text-sm"
          >
            <Sparkles className="w-4 h-4" /> START RESEARCH
          </button>
        </div>
      </form>
    </div>
  );
};
