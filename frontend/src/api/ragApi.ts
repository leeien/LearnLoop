import type {
  KnowledgeDocument,
  KnowledgeDocumentDetail,
  KnowledgeSourceType,
  RAGAnswer,
  RAGQuizResult,
  RAGSearchResult,
} from "../types/models";
import { apiRequest } from "./client";

export interface DocumentInput {
  title: string;
  source_type: KnowledgeSourceType;
  content: string;
  tags: string[];
}

export const ragApi = {
  listDocuments: () =>
    apiRequest<KnowledgeDocument[]>("/api/rag/documents"),

  getDocument: (documentId: number) =>
    apiRequest<KnowledgeDocumentDetail>(
      `/api/rag/documents/${documentId}`,
    ),

  createDocument: (input: DocumentInput) =>
    apiRequest<KnowledgeDocumentDetail>("/api/rag/documents", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  updateDocument: (
    documentId: number,
    input: Partial<DocumentInput>,
  ) =>
    apiRequest<KnowledgeDocumentDetail>(
      `/api/rag/documents/${documentId}`,
      {
        method: "PATCH",
        body: JSON.stringify(input),
      },
    ),

  deleteDocument: (documentId: number) =>
    apiRequest<{ id: number; deleted: boolean }>(
      `/api/rag/documents/${documentId}`,
      { method: "DELETE" },
    ),

  indexDocument: (documentId: number) =>
    apiRequest<{
      document_id: number;
      chunk_count: number;
      embedding_provider: string;
    }>(`/api/rag/documents/${documentId}/index`, {
      method: "POST",
    }),

  search: (query: string, topK = 5) =>
    apiRequest<RAGSearchResult[]>("/api/rag/search", {
      method: "POST",
      body: JSON.stringify({ query, top_k: topK }),
    }),

  ask: (question: string, topK = 5) =>
    apiRequest<RAGAnswer>("/api/rag/ask", {
      method: "POST",
      body: JSON.stringify({ question, top_k: topK }),
    }),

  generateQuiz: (
    documentId: number,
    topic: string,
    questionCount = 5,
  ) =>
    apiRequest<RAGQuizResult>("/api/rag/generate-quiz", {
      method: "POST",
      body: JSON.stringify({
        document_id: documentId,
        topic,
        question_count: questionCount,
      }),
    }),
};
