import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProgressStepper from '../components/ProgressStepper';

const STEPS = [
  'Downloading video payload...',
  'Azure VI processing (Audio/OCR)...',
  'Vector DB compliance lookup...',
  'GPT-4o Policy Analysis...',
  'Compiling final report...'
];

export default function Audit() {
  const [videoUrl, setVideoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fake progress stepper logic while waiting for the single API response
  useEffect(() => {
    let interval;
    if (isLoading) {
      interval = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev < STEPS.length - 1) return prev + 1;
          return prev;
        });
      }, 15000); // Advance step every 15 seconds
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleAudit = async (e) => {
    e.preventDefault();
    if (!videoUrl) return;

    setIsLoading(true);
    setError(null);
    setCurrentStep(0);
    
    const startTime = Date.now();

    try {
      // In production: Vercel's proxy rewrites /audit → Render backend (see vercel.json)
      // In local dev: update frontend/.env with VITE_API_BASE_URL=http://localhost:8000
      const apiBase = (import.meta.env.VITE_API_BASE_URL || '').replace(/^http:\/\/localhost.*/, '');
      const apiUrl = `${apiBase}/audit`;
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'dev_key_tenant_a'
        },
        body: JSON.stringify({ video_url: videoUrl })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      const duration = ((Date.now() - startTime) / 1000).toFixed(1) + 's';
      
      const historyItem = {
        session_id: data.session_id,
        video_url: videoUrl,
        status: data.status,
        date: new Date().toISOString(),
        duration: duration,
        results: data
      };

      // Save to localStorage
      const history = JSON.parse(localStorage.getItem('brand_guardian_history') || '[]');
      localStorage.setItem('brand_guardian_history', JSON.stringify([historyItem, ...history]));

      navigate(`/results/${data.session_id}`, { state: historyItem });
    } catch (err) {
      setError(err.message || 'Failed to connect to the auditing server.');
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ marginBottom: '0.5rem', fontSize: '24px' }}>New Compliance Audit</h1>
      <p className="text-muted" style={{ marginBottom: '2rem' }}>Submit a video URL to scan for brand and regulatory compliance violations.</p>

      <div className="card" style={{ maxWidth: '600px' }}>
        <form onSubmit={handleAudit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '14px' }}>Video URL</label>
            <input 
              type="url" 
              placeholder="https://youtu.be/..." 
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              disabled={isLoading}
              required
            />
          </div>
          
          {error && (
            <div style={{ padding: '0.75rem', backgroundColor: 'var(--color-critical-bg)', color: 'var(--color-critical-text)', borderRadius: '8px', fontSize: '14px' }}>
              <strong>Error:</strong> {error}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
            <button type="submit" className="primary" disabled={isLoading || !videoUrl}>
              {isLoading ? 'Processing Audit...' : 'Run Audit'}
            </button>
          </div>
        </form>

        {isLoading && (
          <div style={{ borderTop: '0.5px solid var(--border-color)', marginTop: '2rem', paddingTop: '1rem' }}>
            <ProgressStepper steps={STEPS} currentStepIndex={currentStep} />
          </div>
        )}
      </div>
    </div>
  );
}
