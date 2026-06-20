import { useLocation, useParams, useNavigate } from 'react-router-dom';
import StatusBadge from '../components/StatusBadge';
import ViolationCard from '../components/ViolationCard';
import StatCard from '../components/StatCard';
import { Download, ArrowLeft } from 'lucide-react';

export default function Results() {
  const { session_id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Either passed from Audit.jsx navigation state or read from history
  const data = location.state;

  if (!data || !data.results) {
    return (
      <div>
        <h2>Report Not Found</h2>
        <p>No data found for session {session_id}.</p>
        <button onClick={() => navigate('/history')}>Back to History</button>
      </div>
    );
  }

  const { status, final_report, compliance_results } = data.results;

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([final_report], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `audit_report_${session_id}.txt`;
    document.body.appendChild(element); // Required for this to work in FireFox
    element.click();
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
        <button onClick={() => navigate(-1)} style={{ padding: '0.5rem', background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-main)' }}>
          <ArrowLeft size={16} />
        </button>
        <h1 style={{ fontSize: '24px' }}>Audit Results</h1>
        <div style={{ marginLeft: 'auto' }}>
          <button onClick={handleDownload} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-main)' }}>
            <Download size={16} /> Download Report
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <StatCard title="Overall Status" value={<StatusBadge status={status} />} />
        <StatCard title="Duration" value={data.duration || 'N/A'} />
        <StatCard title="Violations Found" value={compliance_results?.length || 0} />
      </div>

      <div style={{ display: 'flex', gap: '2rem' }}>
        <div style={{ flex: 2 }}>
          <h2 style={{ fontSize: '18px', marginBottom: '1rem' }}>Detected Violations</h2>
          {compliance_results && compliance_results.length > 0 ? (
            compliance_results.map((v, i) => <ViolationCard key={i} violation={v} />)
          ) : (
            <div className="card text-muted">No compliance violations detected.</div>
          )}
        </div>

        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: '18px', marginBottom: '1rem' }}>AI Summary</h2>
          <div className="card" style={{ whiteSpace: 'pre-wrap', fontSize: '14px', lineHeight: '1.6' }}>
            {final_report || 'No summary generated.'}
          </div>
        </div>
      </div>
    </div>
  );
}
