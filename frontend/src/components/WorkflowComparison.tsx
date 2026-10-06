import React from 'react';
import { ArrowDown, CheckCircle2, ShieldCheck, Zap, Layers } from 'lucide-react';

export const WorkflowComparison: React.FC = () => {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
      <div className="text-center max-w-2xl mx-auto mb-8">
        <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
          Architectural Differentiation
        </span>
        <h2 className="text-2xl font-bold text-slate-900 mt-2">Why E.V.I.D.A. Goes Beyond Standard AI</h2>
        <p className="text-sm text-slate-500 mt-1">
          Comparing traditional LLM chatbot outputs against E.V.I.D.A.'s 14-step claim verification engine.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* General AI Card */}
        <div className="border border-slate-200 rounded-xl p-5 bg-slate-50/50 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-5 h-5 text-slate-400" />
              <h3 className="font-bold text-slate-800 text-base">General AI Assistant</h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Single-prompt completion without domain grounding or citation verification.
            </p>

            <div className="space-y-2 text-xs font-medium text-slate-600 bg-white p-3 rounded-lg border border-slate-200">
              <div className="p-2 bg-slate-100 rounded text-center">User Question</div>
              <ArrowDown className="w-3.5 h-3.5 mx-auto text-slate-400" />
              <div className="p-2 bg-slate-100 rounded text-center">LLM Completion</div>
              <ArrowDown className="w-3.5 h-3.5 mx-auto text-slate-400" />
              <div className="p-2 bg-amber-50 text-amber-800 border border-amber-200 rounded text-center">
                Unverified Direct Answer
              </div>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-200 text-xs text-slate-500">
            ❌ High risk of hallucinated citations and unverified claims.
          </div>
        </div>

        {/* Basic RAG Card */}
        <div className="border border-slate-200 rounded-xl p-5 bg-slate-50/50 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Layers className="w-5 h-5 text-slate-500" />
              <h3 className="font-bold text-slate-800 text-base">Basic RAG Chatbot</h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Simple vector similarity search followed by text summarizing.
            </p>

            <div className="space-y-2 text-xs font-medium text-slate-600 bg-white p-3 rounded-lg border border-slate-200">
              <div className="p-2 bg-slate-100 rounded text-center">User Question</div>
              <ArrowDown className="w-3.5 h-3.5 mx-auto text-slate-400" />
              <div className="p-2 bg-slate-100 rounded text-center">Retrieve Document Chunks</div>
              <ArrowDown className="w-3.5 h-3.5 mx-auto text-slate-400" />
              <div className="p-2 bg-blue-50 text-blue-800 border border-blue-200 rounded text-center">
                Summarized Text Answer
              </div>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-200 text-xs text-slate-500">
            ⚠️ Lacks claim extraction, conflict detection, or source audit.
          </div>
        </div>

        {/* E.V.I.D.A. Card */}
        <div className="border-2 border-blue-600 rounded-xl p-5 bg-gradient-to-b from-blue-50/30 to-white flex flex-col justify-between shadow-md">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-slate-900 text-base">E.V.I.D.A. Platform</h3>
            </div>
            <p className="text-xs text-blue-900 font-medium mb-4">
              Traceable multi-agent research workflow with claim verification.
            </p>

            <div className="space-y-1.5 text-[11px] font-semibold text-slate-700 bg-white p-3 rounded-lg border border-blue-200">
              <div className="p-1.5 bg-blue-50 text-blue-900 rounded text-center">Research Planning Agent</div>
              <div className="p-1.5 bg-slate-50 rounded text-center">pgvector Domain RAG + Web + Memory</div>
              <div className="p-1.5 bg-slate-50 rounded text-center">Atomic Claim Extraction</div>
              <div className="p-1.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded text-center">
                Claim Verification (SUPPORTED / CONFLICT)
              </div>
              <div className="p-1.5 bg-slate-50 rounded text-center">Source Evaluation & Confidence</div>
              <div className="p-1.5 bg-indigo-50 text-indigo-900 rounded text-center font-bold">
                Traceable Report with Clickable Citations
              </div>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-blue-100 text-xs text-blue-700 font-semibold flex items-center gap-1">
            <CheckCircle2 className="w-4 h-4 text-blue-600" /> Every claim linked to exact page and chunk citations.
          </div>
        </div>
      </div>
    </div>
  );
};
