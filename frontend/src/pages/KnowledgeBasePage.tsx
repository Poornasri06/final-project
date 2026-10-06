import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { DocumentItem, KnowledgeBaseStats, DocumentChunkItem } from '../types';
import { X, Plus, Sparkles, Trash2 } from 'lucide-react';

export const KnowledgeBasePage: React.FC = () => {
  const [stats, setStats] = useState<KnowledgeBaseStats | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>('All');
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const [docChunks, setDocChunks] = useState<DocumentChunkItem[]>([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [isSeedingDemo, setIsSeedingDemo] = useState(false);

  // Upload Form State
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadCategory, setUploadCategory] = useState('Diabetes');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    loadData();
  }, [activeCategory]);

  const loadData = async () => {
    try {
      const s = await api.getKnowledgeBaseStats();
      setStats(s);
      const docs = await api.getDocuments(activeCategory);
      setDocuments(docs);
    } catch (e) {
      console.error(e);
    }
  };

  const hasDemoDocs = documents.some((d) => d.is_demo);

  const handleToggleDemoDataset = async () => {
    setIsSeedingDemo(true);
    try {
      if (hasDemoDocs) {
        await api.unloadDemoDataset();
      } else {
        await api.seedDemoDataset();
      }
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSeedingDemo(false);
    }
  };

  const handleSelectDoc = async (doc: DocumentItem) => {
    setSelectedDoc(doc);
    try {
      const chunks = await api.getDocumentChunks(doc.id);
      setDocChunks(chunks);
    } catch (e) {
      console.error(e);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !uploadTitle.trim()) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('title', uploadTitle);
      formData.append('category', uploadCategory);

      await api.uploadDocument(formData);
      setShowUploadModal(false);
      setUploadTitle('');
      setUploadFile(null);
      await loadData();
    } catch (e: any) {
      alert(e.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6 py-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
            Healthcare Knowledge Base
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold border border-emerald-200">
              Database Ready
            </span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Database-backed document management and pgvector structure-aware chunks.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleToggleDemoDataset}
            disabled={isSeedingDemo}
            className={`px-4 py-2.5 font-bold text-xs rounded-xl border transition-colors flex items-center gap-2 ${
              hasDemoDocs
                ? 'bg-amber-100/80 hover:bg-amber-200 text-amber-900 border-amber-300'
                : 'bg-amber-50 hover:bg-amber-100 text-amber-800 border-amber-300'
            }`}
          >
            {hasDemoDocs ? (
              <>
                <Trash2 className="w-4 h-4 text-amber-700" />
                {isSeedingDemo ? 'Unloading Demo Dataset...' : 'Unload Demo Dataset'}
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-amber-600" />
                {isSeedingDemo ? 'Loading Demo Dataset...' : 'Load Demo Dataset'}
              </>
            )}
          </button>

          <button
            onClick={() => setShowUploadModal(true)}
            className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-xs transition-colors flex items-center gap-2"
          >
            <Plus className="w-4 h-4" /> Upload Document
          </button>
        </div>
      </div>

      {/* Database Statistics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Documents</p>
          <p className="text-2xl font-black text-slate-900 mt-1">{stats?.documents_count ?? documents.length}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Indexed Documents</p>
          <p className="text-2xl font-black text-blue-600 mt-1">{stats?.indexed_count ?? documents.length}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Chunks</p>
          <p className="text-2xl font-black text-indigo-600 mt-1">{stats?.chunks_count ?? 0}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Domain</p>
          <p className="text-2xl font-black text-slate-900 mt-1">{stats?.domain ?? 'Healthcare'}</p>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-3">
        {['All', 'Diabetes', 'Cardiovascular Disease', 'Hypertension', 'General Healthcare'].map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeCategory === cat
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Document Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-100/70 border-b border-slate-200 text-xs font-bold text-slate-600 uppercase tracking-wider">
                <th className="py-3.5 px-4">Document Title</th>
                <th className="py-3.5 px-4">Category</th>
                <th className="py-3.5 px-4">Author / Source</th>
                <th className="py-3.5 px-4">Chunks</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-sm">
              {documents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-10 text-center text-slate-500 text-xs">
                    No documents uploaded yet. Upload a PDF/TXT document or click "Load Demo Dataset" to populate demo clinical guidelines.
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-4 px-4 font-semibold text-slate-900 max-w-xs">
                      {doc.title}
                      {doc.is_demo && (
                        <span className="ml-2 text-[10px] bg-amber-100 text-amber-800 border border-amber-200 px-1.5 py-0.5 rounded font-bold">
                          DEMO DATA
                        </span>
                      )}
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-xs bg-slate-100 text-slate-700 px-2.5 py-1 rounded-md font-medium">
                        {doc.category}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-xs text-slate-600">
                      {doc.author || 'Medical Advisory Panel'} ({doc.publication_date || '2025'})
                    </td>
                    <td className="py-4 px-4 font-bold text-slate-700">{doc.chunk_count}</td>
                    <td className="py-4 px-4">
                      <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        {doc.processing_status}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <button
                        onClick={() => handleSelectDoc(doc)}
                        className="text-xs font-bold text-blue-600 hover:text-blue-800 bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-200"
                      >
                        Inspect Chunks
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Document Chunk Inspector */}
      {selectedDoc && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-md space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <div>
              <span className="text-xs font-bold text-blue-600 uppercase">Chunk Visualizer & RAG Inspector</span>
              <h2 className="text-lg font-bold text-slate-900">{selectedDoc.title}</h2>
            </div>
            <button
              onClick={() => setSelectedDoc(null)}
              className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              {docChunks.length} Structure-Aware Chunks
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
              {docChunks.map((chunk) => (
                <div key={chunk.id} className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-1">
                  <div className="flex items-center justify-between text-[11px] text-slate-500 font-semibold">
                    <span>CHUNK #{chunk.chunk_index} • Page {chunk.page_number}</span>
                    <span className="bg-slate-200 text-slate-800 px-1.5 py-0.5 rounded">
                      Sec: {chunk.section}
                    </span>
                  </div>
                  <p className="text-slate-700 italic">"{chunk.text}"</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white max-w-lg w-full rounded-2xl p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <h2 className="text-lg font-bold text-slate-900">Upload Healthcare Document</h2>
              <button onClick={() => setShowUploadModal(false)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Document Title *</label>
                <input
                  type="text"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  placeholder="e.g. Clinical Guidelines for Type 2 Diabetes Management"
                  className="w-full p-2.5 border border-slate-300 rounded-lg text-sm"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Category</label>
                <select
                  value={uploadCategory}
                  onChange={(e) => setUploadCategory(e.target.value)}
                  className="w-full p-2.5 border border-slate-300 rounded-lg text-sm bg-slate-50"
                >
                  <option value="Diabetes">Diabetes</option>
                  <option value="Cardiovascular Disease">Cardiovascular Disease</option>
                  <option value="Hypertension">Hypertension</option>
                  <option value="General Healthcare">General Healthcare</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">File (PDF, TXT, DOCX) *</label>
                <input
                  type="file"
                  accept=".pdf,.txt,.docx"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="w-full p-2 border border-slate-300 rounded-lg text-xs"
                  required
                />
              </div>

              <div className="pt-2 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUploading}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-xs"
                >
                  {isUploading ? 'Processing Chunking...' : 'Upload & Process'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
