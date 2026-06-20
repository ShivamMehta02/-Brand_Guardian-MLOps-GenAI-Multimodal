export default function StatusBadge({ status }) {
  const isCritical = status?.toUpperCase() === 'CRITICAL' || status?.toUpperCase() === 'FAIL';
  const isWarning = status?.toUpperCase() === 'WARNING';
  const isPass = status?.toUpperCase() === 'PASS';

  let bg = '#F3F4F6';
  let color = '#374151';

  if (isCritical) {
    bg = 'var(--color-critical-bg)';
    color = 'var(--color-critical-text)';
  } else if (isWarning) {
    bg = 'var(--color-warning-bg)';
    color = 'var(--color-warning-text)';
  } else if (isPass) {
    bg = 'var(--color-pass-bg)';
    color = 'var(--color-pass-text)';
  }

  return (
    <span style={{
      backgroundColor: bg,
      color: color,
      padding: '4px 8px',
      borderRadius: '8px',
      fontSize: '12px',
      fontWeight: '500',
      display: 'inline-block',
      textTransform: 'uppercase'
    }}>
      {status || 'UNKNOWN'}
    </span>
  );
}
