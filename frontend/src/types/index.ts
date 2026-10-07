export interface DocumentItem {
  id: string;
  title: string;
  domain: string;
  category: string;
  author?: string;
  publication_date?: string;
  source_url?: string;
  description?: string;
  file_size_bytes: number;
  total_pages: number;
  chunk_count: number;
  processing_status: string;
  is_demo: boolean;
  created_at: string;
}

export interface DocumentChunkItem {
  id: string;
  chunk_index: number;
  page_number: number;
  section: string;
  text: string;
  token_count: number;
  domain: string;
}

export interface ClaimEvidenceLink {
  evidence_text: string;
  source_title: string;
  source_url?: string;
  relationship_type: 'SUPPORTED' | 'PARTIALLY_SUPPORTED' | 'UNSUPPORTED' | 'CONTRADICTED';
  section: string;
  page_number: number;
}

export interface ClaimItem {
  id: string;
  claim_text: string;
  claim_type: string;
  subtopic: string;
  importance: string;
  verification_status: 'SUPPORTED' | 'PARTIALLY_SUPPORTED' | 'UNSUPPORTED' | 'CONTRADICTED';
  confidence_score: number;
  summary_reasoning?: string;
  evidence_links: ClaimEvidenceLink[];
}

export interface SourceItem {
  id: string;
  title: string;
  url?: string;
  domain: string;
  source_type: string;
  author?: string;
  publication_date?: string;
  snippet?: string;
  quality_assessment: string;
  quality_explanation?: string;
}

export interface ConflictItem {
  id: string;
  topic: string;
  explanation: string;
  methodological_differences?: string;
}

export interface ConfidenceAssessment {
  overall_confidence: 'HIGH' | 'MODERATE' | 'LOW';
  confidence_score: number;
  supporting_sources_count: number;
  contradictory_sources_count: number;
  unsupported_claims_count: number;
  key_reasons: string[];
}

export interface CritiqueItem {
  unsupported_claims_count: number;
  weak_evidence_count: number;
  conflicts_count: number;
  research_gaps_count: number;
  gaps_description?: string;
  recommendations: string[];
}

export interface ResearchSession {
  id: string;
  title: string;
  question: string;
  domain: string;
  research_depth: string;
  status: string;
  current_step_description: string;
  execution_time_seconds: number;
  created_at: string;
  claims_count: number;
  sources_count: number;
  conflicts_count: number;
  plans?: any[];
  claims?: ClaimItem[];
  sources?: SourceItem[];
  conflicts?: ConflictItem[];
  confidence?: ConfidenceAssessment;
  critique?: CritiqueItem;
  report_id?: string;
}

export interface FormattedReportData {
  language: string;
  language_name: string;
  org_title: string;
  org_subtitle: string;
  report_title: string;
  question: string;
  original_question: string;
  domain: string;
  research_depth: string;
  date: string;
  executive_summary: string;
  methodology_steps: { step: number; title: string; desc: string }[];
  sources: {
    index: number;
    title: string;
    organization: string;
    source_type: string;
    quality: string;
    publication_date: string;
    url: string;
  }[];
  key_findings: { number: number; title: string; description: string; status: string }[];
  claims_table: {
    index: number;
    claim: string;
    evidence: string;
    source: string;
    page: string;
    verification: string;
  }[];
  evidence_breakdown: {
    index: number;
    claim: string;
    evidence: string;
    source: string;
    page: string;
    verification: string;
    reason: string;
  }[];
  source_quality: {
    index: number;
    source_title: string;
    authority: string;
    relevance: string;
    quality_rating?: string;
    evidence_quality?: string;
    publication_info?: string;
    explanation: string;
  }[];
  conflicts: {
    has_conflict?: boolean;
    topic: string;
    evidence_a?: string;
    source_a?: string;
    evidence_b?: string;
    source_b?: string;
    explanation: string;
    methodological_differences?: string;
  }[];
  confidence: {
    rating: string;
    score_percent: number;
    supporting_sources_count: number;
    contradictory_sources_count: number;
    reasons: string[];
  };
  final_answer: {
    summary: string;
    bullet_points: string[];
  };
  limitations: string[];
  disclaimer: string;
}

export interface ReportItem {
  id: string;
  session_id: string;
  title: string;
  executive_summary: string;
  methodology: string;
  full_content_markdown: string;
  created_at: string;
  citations: { citation_number: number; source_id: string; citation_text: string }[];
}

export interface KnowledgeBaseStats {
  dataset_name: string;
  domain: string;
  documents_count: number;
  indexed_count: number;
  chunks_count: number;
  status: string;
  categories: { category: string; count: number }[];
}

export interface EvaluationMetrics {
  status: string;
  benchmark_dataset_loaded: boolean;
  metrics: {
    claim_verification_accuracy: number;
    citation_correctness: number;
    evidence_retrieval_accuracy: number;
    conflict_detection_accuracy: number;
    unsupported_claim_rate: number;
    average_research_time_sec: number;
    average_reflection_cycles: number;
  };
  comparison: {
    baseline_rag: any;
    evida_platform: any;
  };
}
