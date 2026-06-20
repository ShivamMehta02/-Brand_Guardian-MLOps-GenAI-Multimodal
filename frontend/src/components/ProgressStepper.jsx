import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

export default function ProgressStepper({ steps, currentStepIndex }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '2rem' }}>
      {steps.map((step, index) => {
        const isCompleted = index < currentStepIndex;
        const isCurrent = index === currentStepIndex;
        const isPending = index > currentStepIndex;

        let Icon = Circle;
        let color = 'var(--text-muted)';
        let textStyle = { color: 'var(--text-muted)' };

        if (isCompleted) {
          Icon = CheckCircle2;
          color = 'var(--color-pass-text)';
          textStyle = { color: 'var(--text-main)' };
        } else if (isCurrent) {
          Icon = Loader2;
          color = 'var(--accent-blue)';
          textStyle = { color: 'var(--text-main)', fontWeight: '500' };
        }

        return (
          <div key={step} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }} className={isCurrent ? 'fade-in' : ''}>
            <div className={isCurrent ? 'spin' : ''} style={{ display: 'flex', alignItems: 'center' }}>
              <Icon size={20} color={color} className={isCurrent ? 'pulse' : ''} />
            </div>
            <span style={{ fontSize: '14px', ...textStyle }}>{step}</span>
          </div>
        );
      })}
      
      <style>{`
        .spin {
          animation: spin 2s linear infinite;
        }
        @keyframes spin {
          100% { transform: rotate(360deg); }
        }
        .pulse {
          animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: .5; }
        }
      `}</style>
    </div>
  );
}
