import StatusBadge from './StatusBadge';

export default function ViolationCard({ violation }) {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <h3 style={{ fontSize: '16px', color: 'var(--text-main)' }}>{violation.category}</h3>
        <StatusBadge status={violation.severity} />
      </div>
      <p className="text-muted" style={{ margin: 0 }}>{violation.description}</p>
    </div>
  );
}
