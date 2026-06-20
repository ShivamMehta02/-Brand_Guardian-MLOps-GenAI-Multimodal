import { NavLink } from 'react-router-dom';
import { ShieldCheck, History, BarChart2, FileText, Settings } from 'lucide-react';

export default function Sidebar() {
  const navStyle = ({ isActive }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.75rem 1rem',
    color: isActive ? 'var(--accent-blue)' : 'var(--text-muted)',
    backgroundColor: isActive ? 'rgba(24, 95, 165, 0.05)' : 'transparent',
    borderRadius: '8px',
    fontWeight: isActive ? '500' : '400',
    transition: 'all 0.2s'
  });

  return (
    <div style={{
      width: '240px',
      borderRight: '0.5px solid var(--border-color)',
      padding: '2rem 1rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '2rem',
      backgroundColor: 'var(--bg-color)',
      height: '100vh',
      position: 'sticky',
      top: 0
    }}>
      <div style={{ padding: '0 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <ShieldCheck size={24} color="var(--accent-blue)" />
        <h2 style={{ fontSize: '18px' }}>Brand Guardian</h2>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <NavLink to="/" style={navStyle}>
          <ShieldCheck size={18} /> New Audit
        </NavLink>
        <NavLink to="/history" style={navStyle}>
          <History size={18} /> History
        </NavLink>
        <NavLink to="/analytics" style={navStyle} onClick={(e) => e.preventDefault()}>
          <BarChart2 size={18} /> Analytics <span style={{fontSize: '10px', padding: '2px 6px', background: 'var(--border-color)', borderRadius: '4px', marginLeft: 'auto'}}>Beta</span>
        </NavLink>
        <NavLink to="/policies" style={navStyle} onClick={(e) => e.preventDefault()}>
          <FileText size={18} /> Policies
        </NavLink>
        <NavLink to="/settings" style={navStyle} onClick={(e) => e.preventDefault()}>
          <Settings size={18} /> Settings
        </NavLink>
      </nav>
    </div>
  );
}
