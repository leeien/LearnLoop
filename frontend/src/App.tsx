import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/layout/AppLayout";
import DashboardPage from "./pages/DashboardPage";
import HarnessTracePage from "./pages/HarnessTracePage";
import KnowledgeTopicDetailPage from "./pages/KnowledgeTopicDetailPage";
import KnowledgeTopicsPage from "./pages/KnowledgeTopicsPage";
import KnowledgeBasePage from "./pages/KnowledgeBasePage";
import KnowledgeDocumentPage from "./pages/KnowledgeDocumentPage";
import MemoryPage from "./pages/MemoryPage";
import QuizPage from "./pages/QuizPage";
import ReviewPage from "./pages/ReviewPage";
import RAGChatPage from "./pages/RAGChatPage";
import ToolsPage from "./pages/ToolsPage";
import { StudyDataProvider } from "./stores/StudyDataContext";

export default function App() {
  return (
    <StudyDataProvider>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/knowledge" element={<KnowledgeTopicsPage />} />
          <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
          <Route
            path="/knowledge-base/:documentId"
            element={<KnowledgeDocumentPage />}
          />
          <Route path="/rag-chat" element={<RAGChatPage />} />
          <Route
            path="/knowledge/:topicId"
            element={<KnowledgeTopicDetailPage />}
          />
          <Route path="/quiz/:sessionId" element={<QuizPage />} />
          <Route path="/memory" element={<MemoryPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/harness" element={<HarnessTracePage />} />
          <Route path="/tools" element={<ToolsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </StudyDataProvider>
  );
}
