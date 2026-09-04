export type GoalStatus = "pending" | "in_progress" | "completed";
export type TaskStatus = "pending" | "completed" | "skipped";
export type TaskType =
  | "agent_knowledge"
  | "leetcode"
  | "review"
  | "reflection";
export type KnowledgeDifficulty = "beginner" | "intermediate" | "advanced";
export type LeetCodeDifficulty = "easy" | "medium" | "hard";
export type QuizStatus = "pending" | "answered" | "evaluated";
export type QuizQuestionType =
  | "concept"
  | "comparison"
  | "scenario"
  | "pros_cons"
  | "interview";
export type MemoryType =
  | "goal_memory"
  | "completion_memory"
  | "weakness_memory"
  | "mistake_memory"
  | "insight_memory"
  | "review_memory";
export type ReviewReportType = "daily" | "weekly";

export interface DailyGoal {
  id: number;
  date: string;
  title: string;
  description: string;
  status: GoalStatus;
  completion_rate: number;
  created_at: string;
  updated_at: string;
}

export interface LearningTask {
  id: number;
  goal_id: number;
  task_type: TaskType;
  title: string;
  topic: string | null;
  target_count: number;
  current_count: number;
  status: TaskStatus;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeTopic {
  id: number;
  topic_id: string;
  title: string;
  category: string;
  difficulty: KnowledgeDifficulty;
  description: string;
  learning_content: string;
  key_points: string[];
  common_questions: string[];
  mastery_score: number;
  next_review_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface LeetCodeRecord {
  id: number;
  task_id: number;
  problem_number: number;
  problem_title: string;
  difficulty: LeetCodeDifficulty;
  tags: string[];
  is_solved: boolean;
  mistake_reason: string | null;
  insight: string | null;
  need_review: boolean;
  next_review_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DashboardSummary {
  today_goal: DailyGoal | null;
  tasks: {
    total: number;
    pending: number;
    completed: number;
    skipped: number;
  };
  knowledge: {
    total_topics: number;
    average_mastery: number;
  };
  leetcode: {
    total_records: number;
    solved_records: number;
    need_review: number;
  };
}

export interface QuizAnswer {
  id: number;
  quiz_session_id: number;
  question: string;
  question_type: QuizQuestionType;
  user_answer: string | null;
  score: number | null;
  is_passed: boolean | null;
  concept_accuracy: number | null;
  key_points_coverage: number | null;
  engineering_understanding: number | null;
  clarity: number | null;
  strengths: string[] | null;
  weaknesses: string[] | null;
  feedback: string | null;
  corrected_answer: string | null;
  next_review_days: number | null;
  created_at: string;
}

export interface QuizSession {
  id: number;
  task_id: number;
  topic: string;
  status: QuizStatus;
  total_score: number | null;
  is_passed: boolean | null;
  summary: string | null;
  created_at: string;
  evaluated_at: string | null;
  answers: QuizAnswer[];
}

export interface Memory {
  id: number;
  memory_type: MemoryType;
  topic: string;
  content: string;
  source: string;
  importance: number;
  confidence: number;
  next_review_at: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface TopicMastery {
  id: number;
  topic: string;
  category: string;
  mastery_score: number;
  completed_count: number;
  quiz_count: number;
  average_quiz_score: number;
  review_count: number;
  last_reviewed_at: string | null;
  next_review_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReviewReport {
  id: number;
  report_type: ReviewReportType;
  date: string;
  summary: string;
  completed_tasks: string[];
  unfinished_tasks: string[];
  weaknesses: string[];
  insights: string[];
  next_actions: string[];
  created_at: string;
}

export interface ReminderStatus {
  already_reminded: boolean;
  pending_quiz: boolean;
  pending_quiz_session_id: number | null;
  needs_evening_review: boolean;
}

export interface LearningHarnessLog {
  id: number;
  event_type: string;
  entity_type: string;
  entity_id: string;
  input_payload: Record<string, unknown>;
  output_payload: Record<string, unknown>;
  status: string;
  latency_ms: number;
  created_at: string;
}

export type KnowledgeSourceType = "markdown" | "text" | "upload";

export interface KnowledgeChunk {
  id: number;
  document_id: number;
  chunk_index: number;
  content: string;
  embedding_id: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface KnowledgeDocument {
  id: number;
  title: string;
  source_type: KnowledgeSourceType;
  content: string;
  tags: string[];
  chunk_count: number;
  is_indexed: boolean;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeDocumentDetail extends KnowledgeDocument {
  chunks: KnowledgeChunk[];
}

export interface RAGSearchResult {
  chunk_id: number;
  document_id: number;
  document_title: string;
  content: string;
  similarity_score: number;
  metadata: Record<string, unknown>;
}

export interface RAGSource {
  citation: string;
  chunk_id: number;
  document_id: number;
  document_title: string;
  heading: string;
  content: string;
  similarity_score: number;
}

export interface RAGAnswer {
  answer: string;
  has_sufficient_context: boolean;
  sources: RAGSource[];
  retrieved_chunks: RAGSearchResult[];
}

export interface RAGQuizResult {
  quiz_session_id: number;
  task_id: number;
  topic: string;
  questions: Array<{
    id: number;
    question: string;
    question_type: QuizQuestionType;
  }>;
}
