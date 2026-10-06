import React from 'react';
import type { ReportItem } from '../types';
import { ArrowLeft, ExternalLink, ShieldCheck } from 'lucide-react';

interface ReportViewPageProps {
  report: ReportItem | null;
  onBack: () => void;
}

export const ReportViewPage: React.FC<ReportViewPageProps> = ({ report, onBack }) => {
  if (!report) {
    return (
      <div className="py-12 text-center">
        <p className="text-slate-500 text-sm">No report loaded. Please select a research session.</p>
        <button onClick={onBack} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-bold">
          Back to Sessions
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-4">
      {/* Top Bar */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900 font-semibold text-xs bg-white px-3 py-1.5 rounded-lg border border-slate-200"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Research Session
        </button>

        <div className="flex items-center gap-2">
          <span className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1 rounded-full font-bold flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" /> Verified Evidence Report
          </span>
        </div>
      </div>

      {/* Main Report Document Card */}
      <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-md space-y-6">
        <div className="border-b border-slate-200 pb-6">
          <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">
            E.V.I.D.A. Evidence Report
          </span>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 mt-2">{report.title}</h1>
          <p className="text-xs text-slate-400 mt-2">
            Generated on {report.created_at} • Healthcare Research Domain
          </p>
        </div>

        {/* Render Report Sections */}
        <div className="prose prose-slate max-w-none text-slate-800 space-y-6 text-sm leading-relaxed">
          <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Executive Summary</h3>
            <p className="text-slate-800 font-medium text-xs leading-relaxed">{report.executive_summary}</p>
          </div>

          {/* Full Markdown Render */}
          <div className="whitespace-pre-wrap font-sans text-slate-800 space-y-4">
            {report.full_content_markdown}
          </div>
        </div>

        {/* References with Interactive Citation Handlers */}
        <div className="pt-6 border-t border-slate-200 space-y-3">
          <h3 className="text-base font-bold text-slate-900">Traceable References ({report.citations.length})</h3>
          <div className="space-y-2">
            {report.citations.map((cit) => (
              <div
                key={cit.citation_number}
                className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs hover:bg-blue-50/60 cursor-pointer transition-colors flex items-start justify-between"
              >
                <div>
                  <span className="font-bold text-blue-700 mr-2">[{cit.citation_number}]</span>
                  <span className="text-slate-800">{cit.citation_text}</span>
                </div>
                <ExternalLink className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
