import React from 'react';
import { CheckCircle2, Loader2, FileText, ArrowRight } from 'lucide-react';

interface LiveResearchProgressProps {
  statusDescription: string;
  isComplete: boolean;
  onViewReport: () => void;
  onViewMatrix: () => void;
}

export const LiveResearchProgress: React.FC<LiveResearchProgressProps> = ({
  statusDescription,
  isComplete,
  onViewReport,
  onViewMatrix
}) => {
  const steps = [
    { label: 'Question analyzed & intent identified' },
    { label: 'Research plan created with structured subtopics' },
    { label: 'Healthcare documents searched in pgvector' },
    { label: 'Web research APIs searched' },
    { label: 'Previous research memory queried' },
    { label: 'Claims extracted from retrieved context' },
    { label: 'Evidence retrieved & linked to claims' },
    { label: 'Claims verified (SUPPORTED / CONFLICT)' },
    { label: 'Sources evaluated for authority & quality' },
    { label: 'Conflicts checked across independent sources' },
    { label: 'System confidence assessment calculated' },
    { label: 'Research critique & gap analysis completed' },
    { label: 'Reflection loop executed' },
    { label: 'Final traceable research report generated' },
  ];

  return (
    <div className="max-w-3xl mx-auto space-y-6 py-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-md">
        <div className="flex items-center justify-between border-b border-slate-200 pb-4 mb-6">
          <div>
            <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">
              {isComplete ? 'Execution Complete' : 'Live Orchestrator Pipeline'}
            </span>
            <h2 className="text-xl font-bold text-slate-900 mt-1">Multi-Agent Research Session Progress</h2>
          </div>

          {!isComplete ? (
            <div className="flex items-center gap-2 text-xs font-semibold text-blue-700 bg-blue-50 px-3 py-1.5 rounded-full border border-blue-200">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" /> ACTIVE PROCESSING
            </div>
          ) : (
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" /> READY
            </div>
          )}
        </div>

        {/* Current Backend Status Banner */}
        <div className="bg-slate-900 text-white p-4 rounded-xl mb-6 font-mono text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>Backend Status: {statusDescription}</span>
          </div>
        </div>

        {/* Real-time Checklist */}
        <div className="space-y-3">
          {steps.map((step, idx) => {
            const isFinished = isComplete || idx < 12;
            return (
              <div
                key={idx}
                className={`p-3 rounded-lg border flex items-center justify-between text-xs font-medium transition-all ${
                  isFinished
                    ? 'bg-emerald-50/60 border-emerald-200 text-slate-900'
                    : 'bg-slate-50 border-slate-200 text-slate-400'
                }`}
              >
                <div className="flex items-center gap-3">
                  {isFinished ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border-2 border-slate-300 shrink-0" />
                  )}
                  <span>{step.label}</span>
                </div>

                <span className="text-[10px] text-slate-400 font-mono">STEP #{idx + 1}</span>
              </div>
            );
          })}
        </div>

        {/* CTAs upon completion */}
        {isComplete && (
          <div className="mt-8 pt-6 border-t border-slate-200 flex flex-wrap gap-4 justify-end">
            <button
              onClick={onViewMatrix}
              className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold rounded-xl text-sm transition-colors"
            >
              Open Evidence Matrix
            </button>
            
            <button
              onClick={onViewReport}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-sm transition-colors shadow-md flex items-center gap-2"
            >
              <FileText className="w-4 h-4" /> View Full Research Report <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
