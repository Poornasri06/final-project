import React from 'react';
import type { ClaimItem } from '../types';
import { CheckCircle2, AlertTriangle, HelpCircle, XCircle, ChevronRight } from 'lucide-react';

interface EvidenceMatrixProps {
  claims: ClaimItem[];
  onSelectClaim: (claim: ClaimItem) => void;
}

export const EvidenceMatrix: React.FC<EvidenceMatrixProps> = ({ claims, onSelectClaim }) => {
  const getBadgeClass = (status: string) => {
    switch (status) {
      case 'SUPPORTED':
        return 'badge-supported';
      case 'PARTIALLY_SUPPORTED':
        return 'badge-partially-supported';
      case 'UNSUPPORTED':
        return 'badge-unsupported';
      case 'CONTRADICTED':
        return 'badge-contradicted';
      default:
        return 'bg-slate-100 text-slate-700';
    }
  };

  const getBadgeIcon = (status: string) => {
    switch (status) {
      case 'SUPPORTED':
        return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />;
      case 'PARTIALLY_SUPPORTED':
        return <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />;
      case 'UNSUPPORTED':
        return <HelpCircle className="w-3.5 h-3.5 text-slate-500" />;
      case 'CONTRADICTED':
        return <XCircle className="w-3.5 h-3.5 text-rose-600" />;
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
      <div className="p-4 sm:p-6 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            Evidence Matrix
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 font-semibold">
              {claims.length} Extracted Claims
            </span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Interactive claim-by-claim verification matrix linked to clinical source citations and document chunks.
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-100/70 border-b border-slate-200 text-xs font-bold text-slate-600 uppercase tracking-wider">
              <th className="py-3.5 px-4">Claim & Subtopic</th>
              <th className="py-3.5 px-4">Extracted Evidence</th>
              <th className="py-3.5 px-4">Primary Source</th>
              <th className="py-3.5 px-4">Relationship</th>
              <th className="py-3.5 px-4">Confidence</th>
              <th className="py-3.5 px-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 text-sm">
            {claims.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500 text-sm">
                  No claims extracted yet. Run a research query to populate the evidence matrix.
                </td>
              </tr>
            ) : (
              claims.map((claim) => {
                const firstLink = claim.evidence_links[0];
                return (
                  <tr
                    key={claim.id}
                    onClick={() => onSelectClaim(claim)}
                    className="hover:bg-blue-50/50 cursor-pointer transition-colors group"
                  >
                    <td className="py-4 px-4 max-w-xs">
                      <p className="font-semibold text-slate-900 line-clamp-2">{claim.claim_text}</p>
                      <span className="inline-block mt-1 text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                        {claim.subtopic}
                      </span>
                    </td>

                    <td className="py-4 px-4 max-w-sm">
                      {firstLink ? (
                        <p className="text-xs text-slate-600 line-clamp-2 italic">
                          "{firstLink.evidence_text}"
                        </p>
                      ) : (
                        <span className="text-xs text-slate-400 italic">No direct chunk matched</span>
                      )}
                    </td>

                    <td className="py-4 px-4">
                      {firstLink ? (
                        <div>
                          <p className="font-medium text-xs text-slate-800 line-clamp-1">
                            {firstLink.source_title}
                          </p>
                          <p className="text-[11px] text-slate-400">
                            Page {firstLink.page_number} • Sec: {firstLink.section}
                          </p>
                        </div>
                      ) : (
                        <span className="text-xs text-slate-400">N/A</span>
                      )}
                    </td>

                    <td className="py-4 px-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${getBadgeClass(
                          claim.verification_status
                        )}`}
                      >
                        {getBadgeIcon(claim.verification_status)}
                        {claim.verification_status.replace('_', ' ')}
                      </span>
                    </td>

                    <td className="py-4 px-4 font-semibold text-slate-700">
                      {Math.round(claim.confidence_score * 100)}%
                    </td>

                    <td className="py-4 px-4 text-right">
                      <div className="inline-flex items-center gap-1 text-blue-600 group-hover:text-blue-700 text-xs font-semibold">
                        View <ChevronRight className="w-4 h-4" />
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
