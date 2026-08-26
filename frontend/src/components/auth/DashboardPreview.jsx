import React from 'react';
import { useAuth } from '../../context/AuthContext';

export const DashboardPreview = ({ onLogout }) => {
  const { user } = useAuth();

  return (
    <div className="auth-form-panel" style={{ justifyContent: 'flex-start', padding: '2.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div className="preview-badge-success">
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-emerald)', display: 'inline-block' }} />
          Authenticated Session Active
        </div>

        <button
          type="button"
          onClick={onLogout}
          className="auth-toggle-btn"
          style={{ fontSize: '0.85rem', color: 'var(--accent-rose)' }}
        >
          Sign Out ↪
        </button>
      </div>

      <div className="auth-form-header" style={{ marginBottom: '1.25rem' }}>
        <h2>Welcome, {user?.fullName || 'Colleague'}! 👋</h2>
        <p>Your AI workspace is ready. Here is a snapshot of your latest meeting recap.</p>
      </div>

      <div className="meeting-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <div>
            <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)' }}>Sprint Planning & DevOps Architecture</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Recorded Today • 42 mins</span>
          </div>
          <span style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem', background: 'rgba(99, 102, 241, 0.2)', color: 'var(--primary-300)', borderRadius: '4px', fontWeight: 600 }}>
            AI Processed
          </span>
        </div>

        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5', marginBottom: '1rem' }}>
          <strong>Summary:</strong> Team agreed on FastAPI backend architecture, containerized Docker deployments, and Jenkins CI/CD automation pipelines.
        </p>

        <h4 style={{ fontSize: '0.82rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
          Extracted Action Items
        </h4>

        <ul className="action-items-list">
          <li className="action-item">
            <input type="checkbox" defaultChecked className="custom-checkbox" style={{ marginTop: '2px' }} />
            <div>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Frontend Team</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Deliver Login & Register interfaces with responsive styling</div>
            </div>
          </li>
          <li className="action-item">
            <input type="checkbox" className="custom-checkbox" style={{ marginTop: '2px' }} />
            <div>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Backend Team</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Configure FastAPI auth endpoints & Whisper speech-to-text worker</div>
            </div>
          </li>
        </ul>
      </div>

      <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
        <button
          type="button"
          onClick={onLogout}
          className="btn-primary"
          style={{ width: 'auto', padding: '0 1.5rem', margin: '0' }}
        >
          🔐 Return to Sign In
        </button>
      </div>
    </div>
  );
};
