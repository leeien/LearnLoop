import { EmptyGoalState } from "../components/dashboard/EmptyGoalState";
import { DailyReviewSummary } from "../components/dashboard/DailyReviewSummary";
import { KnowledgeProgress } from "../components/dashboard/KnowledgeProgress";
import { LeetCodeTodayList } from "../components/dashboard/LeetCodeTodayList";
import { RecentMemory } from "../components/dashboard/RecentMemory";
import { SummaryCards } from "../components/dashboard/SummaryCards";
import { TodayTaskList } from "../components/dashboard/TodayTaskList";
import { useStudyData } from "../stores/StudyDataContext";
import { isToday } from "../utils/format";

export default function DashboardPage() {
  const {
    todayGoal,
    dashboard,
    leetcodeRecords,
    isLoading,
    error,
  } = useStudyData();
  const todayRecords = leetcodeRecords.filter((record) =>
    isToday(record.created_at),
  );

  return (
    <main className="mx-auto max-w-7xl px-4 pb-48 pt-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm font-medium text-cyan-700">学习概览</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
          今天，继续构建你的 Agent 能力
        </h1>
        <p className="mt-3 text-sm text-slate-500">
          任务打卡、知识进度和学习记录集中在一个工作台。
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          后端请求失败：{error}
        </div>
      )}

      {isLoading ? (
        <div className="grid animate-pulse gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[0, 1, 2, 3].map((item) => (
            <div key={item} className="h-36 rounded-2xl bg-slate-200" />
          ))}
        </div>
      ) : !todayGoal ? (
        <EmptyGoalState />
      ) : (
        <div className="space-y-6">
          <section className="rounded-2xl bg-slate-950 px-6 py-5 text-white">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-cyan-400">
              今日目标
            </p>
            <h2 className="mt-2 text-xl font-semibold">{todayGoal.title}</h2>
            <p className="mt-2 text-sm text-slate-400">
              {todayGoal.description || "保持专注，完成今天的学习任务。"}
            </p>
          </section>

          <SummaryCards
            goal={todayGoal}
            summary={dashboard}
            todayLeetCodeCount={todayRecords.length}
          />

          <div className="grid items-start gap-6 xl:grid-cols-[1.35fr_0.9fr]">
            <div className="space-y-6">
              <TodayTaskList />
              <LeetCodeTodayList records={todayRecords} />
            </div>
            <div className="space-y-6">
              <KnowledgeProgress />
              <RecentMemory />
              <DailyReviewSummary />
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
