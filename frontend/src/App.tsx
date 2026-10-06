import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { LandingPage } from './pages/LandingPage';
import { NewResearchPage } from './pages/NewResearchPage';
import { LiveResearchProgress } from './pages/LiveResearchProgress';
import { EvidenceMatrix } from './components/EvidenceMatrix';
import { ClaimDetailModal } from './components/ClaimDetailModal';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { ReportViewPage } from './pages/ReportViewPage';
import { RAGExplainabilityPage } from './pages/RAGExplainabilityPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { SettingsPage } from './pages/SettingsPage';
import { DashboardPage } from './pages/DashboardPage';
import { api } from './services/api';
import type { ClaimItem, ResearchSession, ReportItem } from './types';

export function App() {
  const [activePage, setActivePage] = useState<string>('landing');
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const [selectedClaim, setSelectedClaim] = useState<ClaimItem | null>(null);

  // Active Research State
  const [currentSession, setCurrentSession] = useState<ResearchSession | null>(null);
  const [currentReport, setCurrentReport] = useState<ReportItem | null>(null);
  const [isResearching, setIsResearching] = useState<boolean>(false);

  // Initial load
  useEffect(() => {
    api.getResearchSessions().then(sessions => {
      if (sessions.length > 0) {
        api.getResearchSessionDetail(sessions[0].id).then(setCurrentSession).catch(console.error);
        api.getResearchReport(sessions[0].id).then(setCurrentReport).catch(console.error);
      }
    }).catch(console.error);
  }, []);

  const handleStartResearch = async (params: any) => {
    setIsResearching(true);
    setActivePage('live-progress');
    try {
      const session = await api.startResearch(params);
      const detail = await api.getResearchSessionDetail(session.id);
      setCurrentSession(detail);

      const report = await api.getResearchReport(session.id);
      setCurrentReport(report);
    } catch (e) {
      console.error('Research execution error:', e);
    } finally {
      setIsResearching(false);
    }
  };

  const handleSelectSessionFromDashboard = async (sessionId: string) => {
    try {
      const detail = await api.getResearchSessionDetail(sessionId);
      setCurrentSession(detail);
      const report = await api.getResearchReport(sessionId);
      setCurrentReport(report);
      setActivePage('report');
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      {/* Top Navbar */}
      <Navbar
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onNavigate={(page) => setActivePage(page)}
      />

      <div className="flex-1 flex max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8">
        {/* Navigation Sidebar */}
        <Sidebar
          activePage={activePage}
          onNavigate={(page) => setActivePage(page)}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Main Content Viewport */}
        <main className="flex-1 min-w-0 py-6 md:pl-6">
          {activePage === 'landing' && (
            <LandingPage onNavigate={(p) => setActivePage(p)} />
          )}

          {activePage === 'new-research' && (
            <NewResearchPage onStartResearch={handleStartResearch} />
          )}

          {activePage === 'live-progress' && (
            <LiveResearchProgress
              statusDescription={currentSession?.current_step_description || 'Pipeline running...'}
              isComplete={!isResearching}
              onViewReport={() => setActivePage('report')}
              onViewMatrix={() => setActivePage('evidence-matrix')}
            />
          )}

          {activePage === 'dashboard' && (
            <DashboardPage
              onNavigate={(p) => setActivePage(p)}
              onSelectSession={handleSelectSessionFromDashboard}
            />
          )}

          {activePage === 'evidence-matrix' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h1 className="text-2xl font-extrabold text-slate-900">Research Evidence Matrix</h1>
                  <p className="text-xs text-slate-500 mt-1">
                    Claim-by-claim verification matrix linked to pgvector document chunks.
                  </p>
                </div>
              </div>

              <EvidenceMatrix
                claims={currentSession?.claims || []}
                onSelectClaim={(claim) => setSelectedClaim(claim)}
              />
            </div>
          )}

          {activePage === 'knowledge-base' && (
            <KnowledgeBasePage />
          )}

          {activePage === 'report' && (
            <ReportViewPage
              report={currentReport}
              onBack={() => setActivePage('dashboard')}
            />
          )}

          {activePage === 'rag-explainability' && (
            <RAGExplainabilityPage />
          )}

          {activePage === 'evaluation' && (
            <EvaluationPage />
          )}

          {activePage === 'settings' && (
            <SettingsPage />
          )}
        </main>
      </div>

      {/* Interactive Claim Detail Modal */}
      <ClaimDetailModal
        claim={selectedClaim}
        onClose={() => setSelectedClaim(null)}
      />
    </div>
  );
}
