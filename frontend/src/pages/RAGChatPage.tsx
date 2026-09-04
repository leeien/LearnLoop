import { useEffect, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { ragApi } from "../api/ragApi";
import { SourceCard } from "../components/rag/SourceCard";
import type {
  KnowledgeDocument,
  RAGAnswer,
} from "../types/models";

export default function RAGChatPage() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<RAGAnswer | null>(null);
  const [documentId, setDocumentId] = useState("");
  const [quizTopic, setQuizTopic] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    ragApi
      .listDocuments()
      .then((items) => {
        setDocuments(items);
        const indexed = items.find((item) => item.is_indexed);
        if (indexed) {
          setDocumentId(String(indexed.id));
          setQuizTopic(indexed.title);
        }
      })
      .catch(() => undefined);
  }, []);

  async function askQuestion(event: FormEvent) {
    event.preventDefault();
    setIsAsking(true);
    setError(null);
    try {
      setAnswer(await ragApi.ask(question.trim(), 5));
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "知识库问答失败",
      );
    } finally {
      setIsAsking(false);
    }
  }

  async function generateQuiz() {
    const numericId = Number(documentId);
    if (!numericId || !quizTopic.trim()) return;
    setIsGenerating(true);
    setError(null);
    try {
      const quiz = await ragApi.generateQuiz(
        numericId,
        quizTopic.trim(),
        5,
      );
      navigate(`/quiz/${quiz.quiz_session_id}`);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "知识库 Quiz 生成失败",
      );
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-4 pb-48 pt-8 sm:px-6 lg:px-8">
      <div>
        <p className="text-sm font-medium text-cyan-700">Grounded QA</p>
        <h1 className="mt-2 text-3xl font-semibold">个人知识库问答</h1>
        <p className="mt-3 text-sm text-slate-500">
          回答必须显示来源；知识库证据不足时不会使用外部知识补答。
        </p>
      </div>

      <form
        onSubmit={(event) => void askQuestion(event)}
        className="mt-8 rounded-2xl bg-slate-950 p-6 text-white"
      >
        <label className="text-sm font-medium" htmlFor="rag-question">
          你的问题
        </label>
        <textarea
          id="rag-question"
          required
          rows={4}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="例如：ReAct 中 Observation 的作用是什么？"
          className="mt-3 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm leading-6 outline-none focus:border-cyan-400"
        />
        <button
          type="submit"
          disabled={isAsking || !question.trim()}
          className="mt-4 rounded-xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 disabled:opacity-50"
        >
          {isAsking ? "检索并回答中…" : "检索知识库"}
        </button>
      </form>

      {error && (
        <div className="mt-5 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error}
        </div>
      )}

      {answer && (
        <div className="mt-6 space-y-6">
          <section className="rounded-2xl border border-slate-200 bg-white p-6">
            <div className="flex items-center justify-between gap-4">
              <h2 className="font-semibold">RAG 回答</h2>
              <span
                className={`rounded-full px-2.5 py-1 text-xs ${
                  answer.has_sufficient_context
                    ? "bg-emerald-50 text-emerald-700"
                    : "bg-amber-50 text-amber-700"
                }`}
              >
                {answer.has_sufficient_context ? "依据充足" : "依据不足"}
              </span>
            </div>
            <p className="mt-4 whitespace-pre-wrap leading-7 text-slate-700">
              {answer.answer}
            </p>
          </section>
          <section>
            <h2 className="font-semibold">引用来源</h2>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              {answer.sources.map((source) => (
                <SourceCard key={source.chunk_id} source={source} />
              ))}
            </div>
          </section>
          <details className="rounded-2xl border border-slate-200 bg-white">
            <summary className="cursor-pointer p-5 font-semibold">
              查看检索到的 Chunks
            </summary>
            <div className="space-y-3 border-t border-slate-200 p-5">
              {answer.retrieved_chunks.map((chunk) => (
                <article key={chunk.chunk_id} className="rounded-xl bg-slate-50 p-4">
                  <p className="text-xs text-slate-500">
                    {chunk.document_title} ·{" "}
                    {(chunk.similarity_score * 100).toFixed(1)}%
                  </p>
                  <p className="mt-2 text-sm leading-6">{chunk.content}</p>
                </article>
              ))}
            </div>
          </details>
        </div>
      )}

      <section className="mt-8 rounded-2xl border border-cyan-200 bg-cyan-50 p-6">
        <h2 className="font-semibold text-cyan-950">基于笔记生成 Quiz</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <select
            value={documentId}
            onChange={(event) => {
              setDocumentId(event.target.value);
              const selected = documents.find(
                (item) => item.id === Number(event.target.value),
              );
              if (selected) setQuizTopic(selected.title);
            }}
            className="rounded-xl border border-cyan-200 bg-white px-4 py-3 text-sm"
          >
            <option value="">选择文档</option>
            {documents.map((document) => (
              <option key={document.id} value={document.id}>
                {document.title}
              </option>
            ))}
          </select>
          <input
            value={quizTopic}
            onChange={(event) => setQuizTopic(event.target.value)}
            placeholder="Quiz Topic"
            className="rounded-xl border border-cyan-200 px-4 py-3 text-sm"
          />
        </div>
        <button
          type="button"
          disabled={isGenerating || !documentId || !quizTopic.trim()}
          onClick={() => void generateQuiz()}
          className="mt-4 rounded-xl bg-cyan-700 px-5 py-3 text-sm font-semibold text-white disabled:opacity-50"
        >
          {isGenerating ? "生成中…" : "生成 5 道检测题"}
        </button>
      </section>
    </main>
  );
}
