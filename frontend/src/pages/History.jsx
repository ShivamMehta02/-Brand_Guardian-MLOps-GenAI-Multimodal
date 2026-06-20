import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import StatusBadge from '../components/StatusBadge';

export default function History() {
  const [history, setHistory] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const saved = localStorage.getItem('brand_guardian_history');
    if (saved) {
      setHistory(JSON.parse(saved));
    }
  }, []);

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem', fontSize: '24px' }}>Audit History</h1>
      
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ backgroundColor: 'rgba(0,0,0,0.02)', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ padding: '1rem', fontSize: '13px', color: 'var(--text-muted)', fontWeight: '500' }}>DATE</th>
              <th style={{ padding: '1rem', fontSize: '13px', color: 'var(--text-muted)', fontWeight: '500' }}>VIDEO URL</th>
              <th style={{ padding: '1rem', fontSize: '13px', color: 'var(--text-muted)', fontWeight: '500' }}>DURATION</th>
              <th style={{ padding: '1rem', fontSize: '13px', color: 'var(--text-muted)', fontWeight: '500' }}>STATUS</th>
              <th style={{ padding: '1rem', fontSize: '13px', color: 'var(--text-muted)', fontWeight: '500' }}>ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {history.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No audit history found. Run your first audit to see it here.
                </td>
              </tr>
            ) : (
              history.map((item, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '1rem', fontSize: '14px' }}>
                    {new Date(item.date).toLocaleDateString()} {new Date(item.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </td>
                  <td style={{ padding: '1rem', fontSize: '14px', maxWidth: '250px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    <a href={item.video_url} target="_blank" rel="noopener noreferrer">{item.video_url}</a>
                  </td>
                  <td style={{ padding: '1rem', fontSize: '14px' }}>{item.duration || '--'}</td>
                  <td style={{ padding: '1rem' }}><StatusBadge status={item.status} /></td>
                  <td style={{ padding: '1rem' }}>
                    <button 
                      onClick={() => navigate(`/results/${item.session_id}`, { state: item })}
                      style={{ padding: '0.5rem 1rem', background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-main)', fontSize: '12px' }}
                    >
                      View Report
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
