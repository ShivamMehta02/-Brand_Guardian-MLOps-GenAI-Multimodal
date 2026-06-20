export default function StatCard({ title, value }) {
  return (
    <div className="card" style={{ flex: 1 }}>
      <h4 className="text-muted" style={{ marginBottom: '0.5rem', fontSize: '13px', textTransform: 'uppercase' }}>{title}</h4>
      <div style={{ fontSize: '24px', fontWeight: '500' }}>{value}</div>
    </div>
  );
}
