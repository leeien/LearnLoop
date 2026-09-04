import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { dashboardApi } from "../api/dashboardApi";
import { goalsApi } from "../api/goalsApi";
import { knowledgeApi } from "../api/knowledgeApi";
import { leetcodeApi } from "../api/leetcodeApi";
import { masteryApi } from "../api/masteryApi";
import { memoryApi } from "../api/memoryApi";
import { reviewApi } from "../api/reviewApi";
import { reminderApi } from "../api/reminderApi";
import { tasksApi } from "../api/tasksApi";
import type {
  DailyGoal,
  DashboardSummary,
  KnowledgeTopic,
  LearningTask,
  LeetCodeRecord,
  Memory,
  ReviewReport,
  ReminderStatus,
  TopicMastery,
} from "../types/models";

interface StudyDataValue {
  todayGoal: DailyGoal | null;
  tasks: LearningTask[];
  dashboard: DashboardSummary | null;
  leetcodeRecords: LeetCodeRecord[];
  knowledgeTopics: KnowledgeTopic[];
  memories: Memory[];
  masteries: TopicMastery[];
  dailyReviews: ReviewReport[];
  reminderStatus: ReminderStatus | null;
  isLoading: boolean;
  error: string | null;
  mutatingTaskId: number | null;
  pendingQuiz: PendingQuiz | null;
  refresh: () => Promise<void>;
  createTodayPlan: () => Promise<void>;
  seedKnowledge: () => Promise<void>;
  completeTask: (taskId: number) => Promise<number | null>;
  skipTask: (taskId: number) => Promise<void>;
  clearPendingQuiz: () => void;
}

interface PendingQuiz {
  sessionId: number;
  taskTitle: string;
}

const StudyDataContext = createContext<StudyDataValue | null>(null);
const PENDING_QUIZ_STORAGE_KEY = "learnloop.pendingQuiz";

function loadPendingQuiz(): PendingQuiz | null {
  const stored = window.localStorage.getItem(PENDING_QUIZ_STORAGE_KEY);
  if (!stored) {
    return null;
  }
  try {
    return JSON.parse(stored) as PendingQuiz;
  } catch {
    window.localStorage.removeItem(PENDING_QUIZ_STORAGE_KEY);
    return null;
  }
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "请求失败，请稍后重试";
}

export function StudyDataProvider({ children }: { children: ReactNode }) {
  const [todayGoal, setTodayGoal] = useState<DailyGoal | null>(null);
  const [tasks, setTasks] = useState<LearningTask[]>([]);
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);
  const [leetcodeRecords, setLeetcodeRecords] = useState<LeetCodeRecord[]>([]);
  const [knowledgeTopics, setKnowledgeTopics] = useState<KnowledgeTopic[]>([]);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [masteries, setMasteries] = useState<TopicMastery[]>([]);
  const [dailyReviews, setDailyReviews] = useState<ReviewReport[]>([]);
  const [reminderStatus, setReminderStatus] =
    useState<ReminderStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mutatingTaskId, setMutatingTaskId] = useState<number | null>(null);
  const [pendingQuiz, setPendingQuiz] = useState<PendingQuiz | null>(
    loadPendingQuiz,
  );

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const [
        goal,
        todayTasks,
        summary,
        records,
        topics,
        memoryItems,
        masteryItems,
        reviewItems,
        reminder,
      ] = await Promise.all([
          goalsApi.getToday(),
          tasksApi.getToday(),
          dashboardApi.getSummary(),
          leetcodeApi.list(),
          knowledgeApi.list(),
          memoryApi.list(),
          masteryApi.list(),
          reviewApi.listDaily(),
          reminderApi.getStatus(),
        ]);
      setTodayGoal(goal);
      setTasks(todayTasks);
      setDashboard(summary);
      setLeetcodeRecords(records);
      setKnowledgeTopics(topics);
      setMemories(memoryItems);
      setMasteries(masteryItems);
      setDailyReviews(reviewItems);
      setReminderStatus(reminder);
    } catch (requestError) {
      setError(errorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    if (reminderStatus && !reminderStatus.already_reminded) {
      void reminderApi.markReminded().then(setReminderStatus).catch(() => {
        // Redis is optional; a failed reminder update must not block study data.
      });
    }
  }, [reminderStatus]);

  const seedKnowledge = useCallback(async () => {
    setError(null);
    try {
      await knowledgeApi.seed();
      await refresh();
    } catch (requestError) {
      setError(errorMessage(requestError));
      throw requestError;
    }
  }, [refresh]);

  const createTodayPlan = useCallback(async () => {
    setError(null);
    try {
      await goalsApi.planToday();
      await refresh();
    } catch (requestError) {
      setError(errorMessage(requestError));
      throw requestError;
    }
  }, [refresh]);

  const completeTask = useCallback(
    async (taskId: number) => {
      setMutatingTaskId(taskId);
      setError(null);
      try {
        const result = await tasksApi.complete(taskId);
        if (result.quiz_session_id !== null) {
          const pending = {
            sessionId: result.quiz_session_id,
            taskTitle: result.task.title,
          };
          setPendingQuiz(pending);
          window.localStorage.setItem(
            PENDING_QUIZ_STORAGE_KEY,
            JSON.stringify(pending),
          );
        }
        await refresh();
        return result.quiz_session_id;
      } catch (requestError) {
        setError(errorMessage(requestError));
        return null;
      } finally {
        setMutatingTaskId(null);
      }
    },
    [refresh],
  );

  const clearPendingQuiz = useCallback(() => {
    setPendingQuiz(null);
    window.localStorage.removeItem(PENDING_QUIZ_STORAGE_KEY);
  }, []);

  const skipTask = useCallback(
    async (taskId: number) => {
      setMutatingTaskId(taskId);
      setError(null);
      try {
        await tasksApi.skip(taskId);
        await refresh();
      } catch (requestError) {
        setError(errorMessage(requestError));
      } finally {
        setMutatingTaskId(null);
      }
    },
    [refresh],
  );

  const value = useMemo(
    () => ({
      todayGoal,
      tasks,
      dashboard,
      leetcodeRecords,
      knowledgeTopics,
      memories,
      masteries,
      dailyReviews,
      reminderStatus,
      isLoading,
      error,
      mutatingTaskId,
      pendingQuiz,
      refresh,
      createTodayPlan,
      seedKnowledge,
      completeTask,
      skipTask,
      clearPendingQuiz,
    }),
    [
      todayGoal,
      tasks,
      dashboard,
      leetcodeRecords,
      knowledgeTopics,
      memories,
      masteries,
      dailyReviews,
      reminderStatus,
      isLoading,
      error,
      mutatingTaskId,
      pendingQuiz,
      refresh,
      createTodayPlan,
      seedKnowledge,
      completeTask,
      skipTask,
      clearPendingQuiz,
    ],
  );

  return (
    <StudyDataContext.Provider value={value}>
      {children}
    </StudyDataContext.Provider>
  );
}

export function useStudyData(): StudyDataValue {
  const value = useContext(StudyDataContext);
  if (value === null) {
    throw new Error("useStudyData must be used within StudyDataProvider");
  }
  return value;
}
