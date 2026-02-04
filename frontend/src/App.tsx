import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { HomePage } from './pages/HomePage';
import { ResumeGeneratorPage } from './pages/ResumeGeneratorPage';
import { LaTeXGeneratorPage } from './pages/LaTeXGeneratorPage';
import { ResumeScreeningPage } from './pages/ResumeScreeningPage';
import { ContentGeneratorPage } from './pages/ContentGeneratorPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ErrorBoundary } from './components/common/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/generate" element={<ResumeGeneratorPage />} />
            <Route path="/latex" element={<LaTeXGeneratorPage />} />
            <Route path="/screen" element={<ResumeScreeningPage />} />
            <Route path="/content" element={<ContentGeneratorPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
