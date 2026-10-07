import React, { useState, useEffect } from 'react';
import type { ReportItem, FormattedReportData } from '../types';
import { api } from '../services/api';
import {
  ArrowLeft, Download, ShieldCheck, ExternalLink, FileText,
  CheckCircle2, AlertTriangle, Loader2
} from 'lucide-react';

interface ReportViewPageProps {
  report: ReportItem | null;
  onBack: () => void;
}

// Helper to clean and format text without raw markdown symbols
const formatClinicalText = (text: string) => {
  if (!text) return null;
  // Replace **bold** with <strong>
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, idx) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={idx} className="font-bold text-slate-900">{part.slice(2, -2)}</strong>;
    }
    return part.replace(/^[#\-*•]\s+/, '');
  });
};

export const ReportViewPage: React.FC<ReportViewPageProps> = ({ report, onBack }) => {
  const [formattedData, setFormattedData] = useState<FormattedReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    if (report?.session_id) {
      loadFormattedReport(report.session_id);
    }
  }, [report?.session_id]);

  const loadFormattedReport = async (sessionId: string) => {
    setLoading(true);
    try {
      const data = await api.getFormattedResearchReport(sessionId, 'en');
      setFormattedData(data);
    } catch (err) {
      console.error('Failed to load formatted report:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!report?.session_id) return;
    setIsDownloading(true);
    try {
      await api.downloadReportPdf(report.session_id, 'en');
    } catch (err) {
      console.error('Download failed:', err);
      alert('Failed to generate and download PDF report. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  if (!report) {
    return (
      <div className="py-16 text-center max-w-lg mx-auto bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
        <FileText className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <h2 className="text-lg font-bold text-slate-800">No Report Selected</h2>
        <p className="text-slate-500 text-xs mt-1">Please select a completed research session from the dashboard.</p>
        <button
          onClick={onBack}
          className="mt-5 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-all shadow-sm"
        >
          Back to Sessions
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 py-4 pb-16">
      {/* Top Action Navigation Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-4 bg-white/80 backdrop-blur-md p-4 rounded-2xl border shadow-xs sticky top-2 z-20">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-slate-700 hover:text-slate-900 font-semibold text-xs bg-slate-100 hover:bg-slate-200 px-3.5 py-2 rounded-xl transition-all cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Research
        </button>

        <div className="flex items-center gap-2.5">
          {/* Direct Download Report Button */}
          <button
            id="btn-download-report"
            onClick={handleDownload}
            disabled={isDownloading}
            className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white font-bold text-xs px-4 py-2 rounded-xl shadow-md hover:shadow-lg transition-all active:scale-95 disabled:opacity-70 cursor-pointer"
          >
            {isDownloading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating PDF...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                Download Report (PDF)
              </>
            )}
          </button>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16 gap-3 text-slate-600 text-xs font-semibold bg-white rounded-3xl border border-slate-200 shadow-sm">
          <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
          Loading clinical evidence report...
        </div>
      )}

      {/* Main Report Document */}
      {!loading && formattedData && (
        <div className="bg-white rounded-3xl border border-slate-200/90 shadow-xl overflow-hidden font-sans">
          
          {/* Document Cover Header */}
          <div className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white p-8 sm:p-10 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
            
            <div className="flex flex-wrap items-center justify-between gap-3 mb-6 relative z-10">
              <div className="flex items-center gap-2">
                <span className="bg-blue-500/20 text-blue-300 border border-blue-400/30 text-[11px] font-extrabold uppercase tracking-widest px-3 py-1 rounded-full">
                  {formattedData.org_title} • Clinical Research Dossier
                </span>
                <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 text-[11px] font-bold px-3 py-1 rounded-full flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" /> Verified Evidence
                </span>
              </div>
              <span className="text-xs text-slate-400 font-medium">
                {formattedData.date}
              </span>
            </div>

            <h1 className="text-xl sm:text-2xl md:text-3xl font-black tracking-tight text-white max-w-3xl leading-snug relative z-10">
              {formattedData.report_title}
            </h1>
            <p className="text-xs text-blue-200 mt-1 relative z-10 font-medium">
              {formattedData.org_subtitle}
            </p>

            {/* Research Question Card */}
            <div className="mt-6 bg-white/10 backdrop-blur-md border border-white/15 p-5 rounded-2xl relative z-10">
              <span className="text-[11px] font-extrabold text-blue-300 uppercase tracking-wider block mb-1">
                RESEARCH QUESTION:
              </span>
              <p className="text-base sm:text-lg font-bold text-white leading-relaxed">
                "{formattedData.question}"
              </p>
              <div className="flex flex-wrap gap-4 mt-3 text-xs text-slate-300 pt-3 border-t border-white/10">
                <span><b>Domain:</b> {formattedData.domain}</span>
                <span><b>Audit Depth:</b> {formattedData.research_depth}</span>
                <span><b>Report Language:</b> English</span>
              </div>
            </div>
          </div>

          <div className="p-8 sm:p-10 space-y-12 text-slate-800 text-sm leading-relaxed">

            {/* SECTION 1: EXECUTIVE SUMMARY */}
            <section className="space-y-3">
              <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight uppercase">
                  1. EXECUTIVE SUMMARY
                </h2>
              </div>
              <div className="bg-blue-50/70 border border-blue-200/80 p-5 rounded-2xl text-slate-900 font-medium text-xs sm:text-sm leading-relaxed shadow-xs">
                {formatClinicalText(formattedData.executive_summary)}
              </div>
            </section>

            {/* SECTION 2: RESEARCH QUESTION */}
            <section className="space-y-3">
              <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight uppercase">
                  2. RESEARCH QUESTION & SCOPE
                </h2>
              </div>
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-2 text-xs sm:text-sm">
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
                  <span className="font-bold text-slate-600">Question:</span>
                  <span className="sm:col-span-3 font-semibold text-slate-900">"{formattedData.question}"</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-200/60">
                  <span className="font-bold text-slate-600">Domain:</span>
                  <span className="sm:col-span-3 text-slate-800">{formattedData.domain}</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-200/60">
                  <span className="font-bold text-slate-600">Research Depth:</span>
                  <span className="sm:col-span-3 text-slate-800">{formattedData.research_depth}</span>
                </div>
              </div>
            </section>

            {/* SECTION 3: RESEARCH METHODOLOGY PIPELINE */}
            <section className="space-y-4">
              <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight uppercase">
                  3. RESEARCH METHODOLOGY PIPELINE
                </h2>
              </div>
              <p className="text-xs text-slate-500">
                Systematic multi-agent evidence verification pipeline flow:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                {formattedData.methodology_steps.map((m, idx) => (
                  <div
                    key={m.step}
                    className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 hover:border-blue-400 hover:bg-blue-50/40 transition-all shadow-2xs relative flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-black text-blue-700 bg-blue-100 px-2 py-0.5 rounded-full">
                          Step {m.step}
                        </span>
                        {idx < formattedData.methodology_steps.length - 1 && (
                          <span className="text-slate-400 text-xs hidden lg:inline">→</span>
                        )}
                      </div>
                      <h4 className="text-xs font-bold text-slate-900 mt-1.5">{m.title}</h4>
                      <p className="text-[11px] text-slate-500 leading-tight mt-1">{m.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* SECTION 4: RESEARCH SOURCES */}
            <section className="space-y-3">
              <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight uppercase">
                  4. RESEARCH SOURCES
                </h2>
              </div>
              <div className="overflow-x-auto rounded-xl border border-slate-200">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-900 text-white font-bold text-[11px]">
                      <th className="py-2.5 px-3 w-10">No.</th>
                      <th className="py-2.5 px-3">Source / Document</th>
                      <th className="py-2.5 px-3 w-36">Organization</th>
                      <th className="py-2.5 px-3 w-28">Source Type</th>
                      <th className="py-2.5 px-3 w-20">Quality</th>
                      <th className="py-2.5 px-3 w-24">Publication Date</th>
                      <th className="py-2.5 px-3 w-28">URL</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {formattedData.sources.map((s, idx) => (
                      <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/70'}>
                        <td className="py-2.5 px-3 font-bold text-slate-500">{s.index}</td>
                        <td className="py-2.5 px-3">
                          <p className="font-bold text-slate-900">{s.title}</p>
                        </td>
                        <td className="py-2.5 px-3 text-slate-600">{s.organization}</td>
                        <td className="py-2.5 px-3 text-slate-600">{s.source_type}</td>
                        <td className="py-2.5 px-3">
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                            {s.quality}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-600">{s.publication_date}</td>
                        <td className="py-2.5 px-3 text-[11px] text-blue-600">
                          {s.url && s.url !== 'Not available' ? (
                            <a href={s.url} target="_blank" rel="noopener noreferrer" className="hover:underline flex items-center gap-1 font-semibold">
                              Link <ExternalLink className="w-3 h-3" />
                            </a>
                          ) : (
                            <span className="text-slate-400">Not available</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* SECTION 5: KEY FINDINGS */}
            <section className="space-y-3">
              <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight uppercase">
                  5. KEY FINDINGS
                </h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {formattedData.key_findings.map((f) => (
                  <div key={f.number} className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-2 shadow-2xs">
                    <div className="flex items-center justify-between border-b border-slate-200/60 pb-1.5">
                      <span className="text-xs font-black text-blue-700">{f.title}</span>
                      <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">
                        {f.status}
                      </span>
                    </div>
                    <p className="text-xs font-medium text-slate-800 leading-relaxed">
                      {formatClinicalText(f.description)}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            {/* SECTION 6: CLAIMS AND EVIDENCE TABLE */}
            <section className="space-y-3">
              <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight uppercase">
                  6. CLAIMS AND EVIDENCE
                </h2>
              </div>
              <div className="overflow-x-auto rounded-xl border border-slate-200">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-900 text-white font-bold text-[11px]">
                      <th className="py-2.5 px-3 w-10">No.</th>
                      <th className="py-2.5 px-3 w-48">Claim</th>
                      <th className="py-2.5 px-3">Supporting Evidence</th>
                      <th className="py-2.5 px-3 w-36">Source</th>
                      <th className="py-2.5 px-3 w-16">Page</th>
                      <th className="py-2.5 px-3 w-28">Verification</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {formattedData.claims_table.map((c, idx) => (
                      <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/70'}>
                        <td className="py-3 px-3 font-bold text-slate-500">{c.index}</td>
                        <td className="py-3 px-3 font-semibold text-slate-900 leading-snug">
                          {formatClinicalText(c.claim)}
                        </td>
                        <td className="py-3 px-3 text-slate-700 leading-relaxed italic">
                          "{formatClinicalText(c.evidence)}"
                        </td>
                        <td className="py-3 px-3 text-slate-600 font-medium">
                          <p className="truncate max-w-[140px]">{c.source}</p>
                        </td>
                        <td className="py-3 px-3 font-semibold text-blue-700">
                          {c.page}
                        </td>
                        <td className="py-3 px-3">
                          <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 inline-block">
                            {c.verification}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* SECTION 7: EVIDENCE VERIFICATION BREAKDOWN */}
            <section className="space-y-3">
              <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight uppercase">
                  7. EVIDENCE VERIFICATION
                </h2>
              </div>
              <div className="space-y-3">
                {formattedData.evidence_breakdown.map((eb) => (
                  <div key={eb.index} className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-2 text-xs">
                    <div className="flex items-center justify-between border-b border-slate-200 pb-1.5">
                      <h4 className="font-bold text-slate-900">
                        Claim #{eb.index}: {formatClinicalText(eb.claim)}
                      </h4>
                      <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">
                        {eb.verification}
                      </span>
                    </div>
                    <p className="text-slate-700">
                      <b>Evidence:</b> "{formatClinicalText(eb.evidence)}"
                    </p>
                    <div className="flex flex-wrap gap-4 text-[11px] text-slate-600 pt-1 border-t border-slate-200/60">
                      <span><b>Source:</b> {eb.source} (Page {eb.page})</span>
                      <span><b>Reason:</b> {formatClinicalText(eb.reason)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* SECTION 8 & 9: SOURCE QUALITY & CONFLICTS */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* SECTION 8: SOURCE QUALITY ASSESSMENT */}
              <section className="space-y-3">
                <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                  <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight uppercase">
                    8. SOURCE QUALITY ASSESSMENT
                  </h2>
                </div>
                <div className="space-y-2.5">
                  {formattedData.source_quality.map((sq) => (
                    <div key={sq.index} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-900 truncate max-w-[200px]">{sq.source_title}</span>
                        <span className="text-[10px] font-bold bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                          {sq.quality_rating || sq.evidence_quality || 'HIGH'}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-600"><b>Authority:</b> {sq.authority}</p>
                      <p className="text-[11px] text-slate-500 leading-snug">{sq.explanation}</p>
                    </div>
                  ))}
                </div>
              </section>

              {/* SECTION 9: CONFLICTING EVIDENCE */}
              <section className="space-y-3">
                <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                  <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight uppercase">
                    9. CONFLICTING EVIDENCE
                  </h2>
                </div>
                <div className="space-y-2.5">
                  {formattedData.conflicts.map((c, idx) => (
                    <div key={idx} className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 text-xs">
                      <h4 className="font-bold text-slate-900">{c.topic}</h4>
                      <p className="text-slate-700 leading-snug">{c.explanation}</p>
                      {c.methodological_differences && (
                        <p className="text-[11px] text-slate-500 italic pt-1 border-t border-slate-200/60">
                          {c.methodological_differences}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            </div>

            {/* SECTION 10: CONFIDENCE ASSESSMENT */}
            <section className="space-y-3">
              <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight uppercase">
                  10. CONFIDENCE ASSESSMENT
                </h2>
              </div>
              <div className="p-5 bg-emerald-50/70 border border-emerald-200 rounded-2xl space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider block">
                      Overall System Confidence
                    </span>
                    <span className="text-2xl font-black text-emerald-950">
                      {formattedData.confidence.rating} ({formattedData.confidence.score_percent}%)
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-xs font-medium text-emerald-900">
                    <span><b>Supporting Sources:</b> {formattedData.confidence.supporting_sources_count}</span>
                    <span><b>Contradictory:</b> {formattedData.confidence.contradictory_sources_count}</span>
                  </div>
                </div>
                <ul className="space-y-1.5 text-xs text-emerald-900 pt-2 border-t border-emerald-200/60">
                  {formattedData.confidence.reasons.map((r, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>{formatClinicalText(r)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </section>

            {/* SECTION 11: FINAL ANSWER */}
            <section className="space-y-3">
              <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
                <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight uppercase">
                  11. FINAL ANSWER
                </h2>
              </div>
              <div className="p-6 bg-slate-900 text-white rounded-2xl space-y-4 shadow-md">
                <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-medium">
                  {formatClinicalText(formattedData.final_answer.summary)}
                </p>
                <div className="space-y-2.5 pt-2 border-t border-slate-800">
                  {formattedData.final_answer.bullet_points.map((bp, idx) => (
                    <div key={idx} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-300">
                      <span className="text-blue-400 font-bold mt-0.5">•</span>
                      <span>{formatClinicalText(bp)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* SECTION 12 & 13: LIMITATIONS & DISCLAIMER */}
            <div className="space-y-6">
              {/* SECTION 12: LIMITATIONS */}
              <section className="space-y-2">
                <h3 className="text-xs font-bold text-slate-600 uppercase tracking-wider">
                  12. LIMITATIONS
                </h3>
                <ul className="space-y-1.5 text-xs text-slate-600">
                  {formattedData.limitations.map((lim, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-slate-400">•</span>
                      <span>{formatClinicalText(lim)}</span>
                    </li>
                  ))}
                </ul>
              </section>

              {/* SECTION 13: MEDICAL DISCLAIMER */}
              <div className="p-5 bg-amber-50 border border-amber-200 rounded-2xl flex items-start gap-3.5 text-xs text-amber-900">
                <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-xs uppercase tracking-wider mb-1 text-amber-950">
                    13. MEDICAL DISCLAIMER
                  </h4>
                  <p className="leading-relaxed font-medium">{formattedData.disclaimer}</p>
                </div>
              </div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
