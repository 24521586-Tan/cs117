import { BrowserRouter, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import AuthCallbackPage from "./pages/AuthCallbackPage";
import HistoryPage from "./pages/HistoryPage";
import JobPage from "./pages/JobPage";
import LoginPage from "./pages/LoginPage";
import UploadPage from "./pages/UploadPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route
          path="/upload"
          element={
            <ProtectedRoute>
              <UploadPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/jobs"
          element={
            <ProtectedRoute>
              <HistoryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/jobs/:id"
          element={
            <ProtectedRoute>
              <JobPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
