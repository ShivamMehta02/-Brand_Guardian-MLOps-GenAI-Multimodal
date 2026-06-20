import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Audit from './pages/Audit';
import Results from './pages/Results';
import History from './pages/History';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Audit />} />
            <Route path="/results/:session_id" element={<Results />} />
            <Route path="/history" element={<History />} />
            <Route path="*" element={<Audit />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
