import React from 'react';
import { WorkflowComparison } from '../components/WorkflowComparison';
import { ShieldCheck, Search, Activity, BookOpen, CheckCircle2 } from 'lucide-react';

interface LandingPageProps {
  onNavigate: (page: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate }) => {
  return (
    <div className="space-y-12 py-6">
      {/* Hero Section */}
      <div className="text-center max-w-4xl mx-auto space-y-6 pt-4">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-slate-700 text-teal-300 text-xs font-bold shadow-xs">
          <Activity className="w-3.5 h-3.5 text-teal-400" /> DEMONSTRATION DOMAIN: HEALTHCARE RESEARCH
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
          Research with Evidence. <br />
          <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-teal-600 bg-clip-text text-transparent">
            Verify Every Single Claim.
          </span>
        </h1>

        <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed font-normal">
          E.V.I.D.A. is an evidence-centric AI research platform that retrieves clinical literature, extracts factual claims, detects conflicting sources, and builds fully traceable research reports.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <button
            onClick={() => onNavigate('new-research')}
            className="px-6 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-blue-500/25 transition-all flex items-center gap-2 text-sm active:scale-95"
          >
            <Search className="w-4 h-4" /> Start Research Session
          </button>
          
          <button
            onClick={() => onNavigate('knowledge-base')}
            className="px-6 py-3.5 bg-white hover:bg-slate-50 text-slate-800 font-bold rounded-xl border border-slate-200/80 transition-all text-sm flex items-center gap-2 shadow-xs hover:border-slate-300"
          >
            <BookOpen className="w-4 h-4 text-teal-600" /> Explore Healthcare Corpus
          </button>
        </div>
      </div>

      {/* Mandatory Core Project Statement Callout */}
      <div className="max-w-4xl mx-auto bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white p-6 sm:p-8 rounded-2xl shadow-xl relative overflow-hidden border border-slate-800">
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 space-y-3">
          <div className="flex items-center gap-2 text-teal-300 text-xs font-bold uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4 text-teal-400" /> Core Product Principle
          </div>
          <blockquote className="text-base sm:text-lg font-medium leading-relaxed italic text-slate-100">
            "E.V.I.D.A. is a domain-specific evidence-centric research platform that goes beyond conventional RAG by connecting claims with supporting or conflicting evidence, evaluating source quality, generating transparent confidence assessments, and producing traceable research reports."
          </blockquote>
        </div>
      </div>

      {/* Interactive Workflow Comparison Section */}
      <WorkflowComparison />

      {/* Feature Highlights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
        <div 
          onClick={() => onNavigate('evidence-matrix')}
          className="bg-white p-6 rounded-2xl border border-slate-200/80 hover:border-emerald-500/50 hover:shadow-xl hover:-translate-y-0.5 transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200/60 text-emerald-600 flex items-center justify-center font-bold mb-4 shadow-xs">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-base group-hover:text-emerald-700 transition-colors">
            Traceable Evidence Matrix
          </h3>
          <p className="text-xs text-slate-500 mt-2 leading-relaxed font-medium">
            Classifies claims into SUPPORTED, PARTIALLY SUPPORTED, or CONTRADICTED with direct links to document section and page numbers.
          </p>
        </div>

        <div 
          onClick={() => onNavigate('rag-explainability')}
          className="bg-white p-6 rounded-2xl border border-slate-200/80 hover:border-indigo-500/50 hover:shadow-xl hover:-translate-y-0.5 transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-200/60 text-indigo-600 flex items-center justify-center font-bold mb-4 shadow-xs">
            <BookOpen className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-base group-hover:text-indigo-700 transition-colors">
            RAG Explainability
          </h3>
          <p className="text-xs text-slate-500 mt-2 leading-relaxed font-medium">
            Inspect dense vector embeddings, cosine similarity scoring, and top-ranked context chunk assembly in real time.
          </p>
        </div>

        <div 
          onClick={() => onNavigate('evaluation')}
          className="bg-white p-6 rounded-2xl border border-slate-200/80 hover:border-blue-500/50 hover:shadow-xl hover:-translate-y-0.5 transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-200/60 text-blue-600 flex items-center justify-center font-bold mb-4 shadow-xs">
            <Activity className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 text-base group-hover:text-blue-700 transition-colors">
            Academic Benchmark Suite
          </h3>
          <p className="text-xs text-slate-500 mt-2 leading-relaxed font-medium">
            Quantitative evaluation metrics comparing Baseline RAG against E.V.I.D.A. across claim accuracy, citation correctness, and conflict detection.
          </p>
        </div>
      </div>
    </div>
  );
};
