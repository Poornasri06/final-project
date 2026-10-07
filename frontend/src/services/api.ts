import type {
  DocumentItem, DocumentChunkItem, ResearchSession, ReportItem, FormattedReportData,
  KnowledgeBaseStats, EvaluationMetrics
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  // Knowledge Base & Stats
  async getKnowledgeBaseStats(): Promise<KnowledgeBaseStats> {
    const res = await fetch(`${API_BASE_URL}/knowledge-base/stats`);
    if (!res.ok) throw new Error('Failed to fetch knowledge base stats');
    return res.json();
  },

  async syncKnowledgeBase(): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/knowledge-base/sync`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to sync knowledge base');
  },

  async seedDemoDataset(): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/knowledge-base/sync`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to sync knowledge base');
  },

  async unloadDemoDataset(): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/knowledge-base/unload-demo`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to unload demo dataset');
  },

  // Documents
  async getDocuments(category?: string): Promise<DocumentItem[]> {
    const url = category && category !== 'All' 
      ? `${API_BASE_URL}/documents?category=${encodeURIComponent(category)}`
      : `${API_BASE_URL}/documents`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async getDocumentChunks(documentId: string): Promise<DocumentChunkItem[]> {
    const res = await fetch(`${API_BASE_URL}/documents/${documentId}/chunks`);
    if (!res.ok) throw new Error('Failed to fetch document chunks');
    return res.json();
  },

  async uploadDocument(formData: FormData): Promise<DocumentItem> {
    const res = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Document upload failed');
    }
    return res.json();
  },

  async deleteDocument(documentId: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete document');
  },

  // Research
  async startResearch(payload: {
    question: string;
    domain?: string;
    research_depth?: string;
    use_knowledge_base?: boolean;
    use_web_search?: boolean;
    use_memory?: boolean;
    category_filter?: string;
  }): Promise<ResearchSession> {
    const res = await fetch(`${API_BASE_URL}/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to start research session');
    return res.json();
  },

  async getResearchSessions(): Promise<ResearchSession[]> {
    const res = await fetch(`${API_BASE_URL}/research`);
    if (!res.ok) throw new Error('Failed to fetch research sessions');
    return res.json();
  },

  async getResearchSessionDetail(id: string): Promise<ResearchSession> {
    const res = await fetch(`${API_BASE_URL}/research/${id}`);
    if (!res.ok) throw new Error('Failed to fetch research session details');
    return res.json();
  },

  async getResearchReport(id: string): Promise<ReportItem> {
    const res = await fetch(`${API_BASE_URL}/research/${id}/report`);
    if (!res.ok) throw new Error('Failed to fetch research report');
    return res.json();
  },

  async getFormattedResearchReport(id: string, lang: string = 'en'): Promise<FormattedReportData> {
    const res = await fetch(`${API_BASE_URL}/research/${id}/formatted-report?lang=${lang}`);
    if (!res.ok) throw new Error('Failed to fetch formatted research report');
    return res.json();
  },

  getReportPdfUrl(id: string, lang: string = 'en'): string {
    return `${API_BASE_URL}/research/${id}/pdf?lang=${lang}`;
  },

  async downloadReportPdf(id: string, lang: string = 'en'): Promise<void> {
    const url = `${API_BASE_URL}/research/${id}/pdf?lang=${lang}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to generate PDF report');
    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = `EVIDA_Clinical_Report_${id.slice(0, 8)}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(blobUrl);
  },

  // Evaluation
  async getEvaluationMetrics(): Promise<EvaluationMetrics> {
    const res = await fetch(`${API_BASE_URL}/evaluation/metrics`);
    if (!res.ok) throw new Error('Failed to fetch evaluation metrics');
    return res.json();
  },

  // Memory
  async getMemoryItems(): Promise<any[]> {
    const res = await fetch(`${API_BASE_URL}/memory`);
    if (!res.ok) throw new Error('Failed to fetch memory items');
    return res.json();
  }
};
