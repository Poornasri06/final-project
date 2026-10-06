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
