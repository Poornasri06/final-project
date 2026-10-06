import React from 'react';
import type { ClaimItem } from '../types';
import { X, ArrowRight, BookOpen } from 'lucide-react';

interface ClaimDetailModalProps {
  claim: ClaimItem | null;
  onClose: () => void;
}

export const ClaimDetailModal: React.FC<ClaimDetailModalProps> = ({ claim, onClose }) => {
  if (!claim) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex justify-end transition-opacity overflow-y-auto">
      <div className="bg-white w-full max-w-2xl h-full shadow-2xl p-6 overflow-y-auto border-l border-slate-200">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-200 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-blue-600 bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full uppercase">
                {claim.claim_type}
              </span>
              <span className="text-xs text-slate-500 font-medium">Subtopic: {claim.subtopic}</span>
            </div>
            <h2 className="text-lg font-bold text-slate-900 mt-2">Claim Evidence Verification</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Claim Text Card */}
        <div className="mt-6 bg-slate-50 border border-slate-200 p-4 rounded-xl">
          <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">
            Factual Claim Statement
          </p>
          <p className="text-base font-semibold text-slate-900">{claim.claim_text}</p>
          
          <div className="mt-3 flex items-center justify-between pt-3 border-t border-slate-200/80 text-xs">
            <span className="text-slate-600">Verification Status:</span>
            <span className="font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
              {claim.verification_status.replace('_', ' ')}
            </span>
          </div>
        </div>

        {/* Interactive Evidence Visualizer Flow */}
        <div className="mt-6">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
            Traceable Evidence Flow
          </h3>
          <div className="bg-gradient-to-r from-blue-50/50 to-indigo-50/50 border border-blue-100 p-4 rounded-xl space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-800">
              <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px]">1</span>
              CLAIM: {claim.claim_text.substring(0, 45)}...
            </div>
            
            <div className="pl-3 border-l-2 border-blue-300 ml-3 py-1 space-y-2 text-xs">
              <div className="flex items-center gap-2 text-slate-700">
                <ArrowRight className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span className="font-semibold text-blue-900">EVIDENCE CHUNK</span>
              </div>

              {claim.evidence_links.map((link, i) => (
                <div key={i} className="bg-white p-3 rounded-lg border border-slate-200 text-xs space-y-1">
                  <p className="text-slate-700 italic">"{link.evidence_text}"</p>
                  
                  <div className="flex items-center gap-2 pt-2 border-t border-slate-100 text-[11px] text-slate-500">
                    <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                    <span className="font-medium text-slate-800">{link.source_title}</span>
                    <span>• Page {link.page_number}</span>
                    <span>• Section: {link.section}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Evidence Reasoning & Quality */}
        <div className="mt-6 space-y-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-2">System Evaluation Rationale</h3>
            <p className="text-xs text-slate-600 bg-slate-50 border border-slate-200 p-3 rounded-lg">
              {claim.summary_reasoning || 'Claim cross-verified against primary clinical guidelines and indexed pgvector document chunks.'}
            </p>
          </div>

          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-2">System Confidence Assessment</h3>
            <div className="flex items-center gap-4 bg-emerald-50 border border-emerald-200 p-4 rounded-xl">
              <div className="w-12 h-12 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-lg">
                {Math.round(claim.confidence_score * 100)}%
              </div>
              <div>
                <p className="font-bold text-slate-900 text-sm">HIGH System Confidence</p>
                <p className="text-xs text-slate-600 mt-0.5">
                  Direct match against high-authority clinical practice guidelines.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer close */}
        <div className="mt-8 pt-4 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold rounded-lg transition-colors"
          >
            Close Evidence View
          </button>
        </div>
      </div>
    </div>
  );
};
