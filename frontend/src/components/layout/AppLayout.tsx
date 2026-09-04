import { NavLink, Outlet } from "react-router-dom";

import { FloatingStudyWidget } from "../floating/FloatingStudyWidget";

const navItems = [
  { to: "/", label: "今日学习", end: true },
  { to: "/knowledge", label: "知识主题", end: false },
  { to: "/knowledge-base", label: "个人知识库", end: false },
  { to: "/rag-chat", label: "RAG 问答", end: false },
  { to: "/memory", label: "长期记忆", end: false },
  { to: "/review", label: "每日复盘", end: false },
  { to: "/harness", label: "学习 Trace", end: false },
  { to: "/tools", label: "Memory Tools", end: false },
];

export function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-4 py-4 sm:px-6 lg:px-8">
          <NavLink to="/" className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-slate-950 text-sm font-bold text-cyan-300">
              AC
            </span>
            <div>
              <p className="text-sm font-semibold leading-none">LearnLoop</p>
              <p className="mt-1 text-xs text-slate-500">学习监督工作台</p>
            </div>
          </NavLink>

          <nav className="flex max-w-[70vw] items-center overflow-x-auto rounded-xl bg-slate-100 p-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm font-medium transition ${
                    isActive
                      ? "bg-white text-slate-950 shadow-sm"
                      : "text-slate-500 hover:text-slate-900"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <Outlet />
      <FloatingStudyWidget />
    </div>
  );
}
