import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

export const DashboardView = ({ onNavigateLogin, onNavigateRegister }) => {
  const { user, logout, showToast } = useAuth();

  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackProgress, setPlaybackProgress] = useState(34);
  const [searchQuery, setSearchQuery] = useState('');

  // Sample Interactive Action Items state
  const [actionItems, setActionItems] = useState([
    {
      id: 1,
      title: 'Deliver interactive Login & Register interfaces with demo switcher',
      assignee: 'Frontend Team',
      dueDate: 'Today',
      completed: true,
    },
    {
      id: 2,
      title: 'Configure FastAPI auth endpoints & Whisper speech-to-text worker',
      assignee: 'Backend Team',
      dueDate: 'Tomorrow',
      completed: false,
    },
    {
      id: 3,
      title: 'Implement speaker diarization pipeline with pyannote.audio',
      assignee: 'ML / AI Team',
      dueDate: 'Aug 20',
      completed: false,
    },
    {
      id: 4,
      title: 'Set up Jenkins CI/CD pipeline and Docker container manifests',
      assignee: 'DevOps Lead',
      dueDate: 'Aug 22',
      completed: false,
    },
  ]);

  const toggleActionItem = (id) => {
    setActionItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, completed: !item.completed } : item
      )
    );
    showToast('info', 'Task Updated', 'Action item status updated.');
  };

  const handlePlayToggle = () => {
    setIsPlaying((prev) => !prev);
    if (!isPlaying) {
      showToast('info', 'Audio Playback', 'Simulating synchronized meeting playback.');
      setPlaybackProgress((prev) => (prev >= 90 ? 10 : prev + 15));
    }
  };

  const handleQuickAction = (actionName) => {
    showToast('success', actionName, `Initiated ${actionName} simulation in demo mode.`);
  };

  const handleSignOut = () => {
    logout();
    if (onNavigateLogin) {
      onNavigateLogin();
    }
  };

  // Sample transcript data
  const transcriptData = [
    {
      speaker: 'Alex Chen',
      role: 'Product Lead',
      avatarColor: 'var(--primary-500)',
      time: '00:04',
      text: 'Good morning everyone. Today we need to align on the AI Meeting Assistant roadmap, specifically the frontend navigation flow and backend AI processing architecture.',
    },
    {
      speaker: 'Sarah Connor',
      role: 'Tech Lead',
      avatarColor: 'var(--accent-cyan)',
      time: '01:18',
      text: 'On the frontend, we have verified seamless navigation between Sign In, Sign Up, and this live Dashboard demo so the entire product flow can be showcased without requiring live database credentials.',
    },
    {
      speaker: 'David Miller',
      role: 'DevOps Engineer',
      avatarColor: 'var(--accent-emerald)',
      time: '02:45',
      text: 'The Docker containers and Jenkins pipelines are structured to deploy the FastAPI backend service alongside our Whisper model inference server once we transition from demo to staging.',
    },
    {
      speaker: 'Alex Chen',
      role: 'Product Lead',
      avatarColor: 'var(--primary-500)',
      time: '04:10',
      text: 'Excellent. Action items are generated automatically and summary points are extracted in real-time. Let’s proceed with validating all user flows.',
    },
  ];

  const filteredTranscript = transcriptData.filter(
    (t) =>
      t.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.speaker.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="dashboard-layout">
      {/* Top Header & Quick Action Controls */}
      <div className="dashboard-header">
        <div className="dashboard-title-area">
          <h1>
            <span>🎙️ AI Workspace Dashboard</span>
            <span className="ai-engine-tag">
              <span className="demo-mode-dot" />
              Whisper AI v3 Active
            </span>
          </h1>
          <p>
            Welcome back, <strong>{user?.fullName || 'Demo Presenter'}</strong>! Real-time audio transcription and automated action item extraction.
          </p>
        </div>

        <div className="dashboard-controls">
          <button
            type="button"
            className="btn-record"
            onClick={() => handleQuickAction('Live Recording')}
            id="btn-start-recording"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="10" />
            </svg>
            <span>New Live Meeting</span>
          </button>

          <button
            type="button"
            className="btn-secondary"
            onClick={() => handleQuickAction('Audio Upload')}
            id="btn-upload-audio"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" x2="12" y1="3" y2="15" />
            </svg>
            <span>Upload Audio</span>
          </button>

          <button
            type="button"
            className="btn-outline-nav"
            onClick={handleSignOut}
            id="btn-dashboard-signout"
          >
            <span>Sign Out ↪</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon-wrap indigo">🎙️</div>
          <div className="metric-info">
            <span className="metric-label">Meetings Processed</span>
            <span className="metric-value">28</span>
            <span className="metric-sub">+4 this week</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap cyan">⏱️</div>
          <div className="metric-info">
            <span className="metric-label">Audio Transcribed</span>
            <span className="metric-value">46.5 hrs</span>
            <span className="metric-sub">Avg 99.2% clarity</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap emerald">✅</div>
          <div className="metric-info">
            <span className="metric-label">Action Items</span>
            <span className="metric-value">
              {actionItems.filter((i) => i.completed).length} / {actionItems.length}
            </span>
            <span className="metric-sub">Synchronized with Jira</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap violet">⚡</div>
          <div className="metric-info">
            <span className="metric-label">STT Accuracy Score</span>
            <span className="metric-value">99.4%</span>
            <span className="metric-sub">FastAPI Worker Ready</span>
          </div>
        </div>
      </div>

      {/* Main 2-Column Dashboard Grid */}
      <div className="dashboard-main-grid">
        {/* Left Column: Meeting Details, Audio Player, Transcript, AI Summary */}
        <div className="meeting-detail-panel">
          <div className="meeting-meta-header">
            <div>
              <h2 className="meeting-title">Sprint Planning & Architecture Sync</h2>
              <div className="meeting-date-pill">
                <span>📅 Recorded Today • 42m 18s</span>
                <span>•</span>
                <span>👥 3 Attendees</span>
              </div>
            </div>

            <button
              type="button"
              className="btn-secondary"
              style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
              onClick={() => handleQuickAction('Export Summary PDF')}
            >
              📥 Export Recap
            </button>
          </div>

          {/* Interactive Audio Player Widget */}
          <div className="audio-player-widget">
            <div className="audio-controls-row">
              <button
                type="button"
                className="audio-play-btn"
                onClick={handlePlayToggle}
                title={isPlaying ? 'Pause Audio' : 'Play Simulated Audio'}
              >
                {isPlaying ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <rect x="6" y="4" width="4" height="16" />
                    <rect x="14" y="4" width="4" height="16" />
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                )}
              </button>

              <div className="audio-timeline-wrap">
                <div className="audio-time-label">
                  <span>{isPlaying ? '14:22' : '04:10'}</span>
                  <span>42:18</span>
                </div>
                <div
                  className="audio-progress-bar"
                  onClick={() => setPlaybackProgress((prev) => (prev + 20) % 100)}
                >
                  <div
                    className="audio-progress-fill"
                    style={{ width: `${playbackProgress}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Simulated Live Audio Wave */}
            <div className="wave-bars" style={{ height: '24px', margin: 0 }}>
              {[...Array(24)].map((_, i) => (
                <div
                  key={i}
                  className="wave-bar"
                  style={{
                    animationPlayState: isPlaying ? 'running' : 'paused',
                    animationDuration: `${0.8 + (i % 5) * 0.2}s`,
                  }}
                />
              ))}
            </div>
          </div>

          {/* AI Structured Summary */}
          <div className="ai-summary-card">
            <h4>
              <span>✨</span>
              <span>AI Executive Summary & Decisions</span>
            </h4>
            <ul>
              <li>
                <strong>Frontend:</strong> Successfully enabled frictionless demo navigation across Sign Up, Login, and Dashboard without backend dependency.
              </li>
              <li>
                <strong>Backend:</strong> FastAPI auth contracts and Whisper transcription workers ready for local/cloud deployment.
              </li>
              <li>
                <strong>DevOps:</strong> Containerized Docker configurations prepared with Jenkins automation pipelines.
              </li>
            </ul>
          </div>

          {/* Diarized Conversation Transcript */}
          <div className="transcript-section">
            <div className="section-subheading">
              <span>Diarized Live Transcript</span>
              <input
                type="text"
                placeholder="Search transcript..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.3rem 0.6rem',
                  color: 'var(--text-primary)',
                  fontSize: '0.78rem',
                  width: '180px',
                }}
              />
            </div>

            <div className="transcript-feed">
              {filteredTranscript.map((item, idx) => (
                <div key={idx} className="transcript-block">
                  <div className="speaker-row">
                    <div className="speaker-badge">
                      <div
                        className="speaker-avatar"
                        style={{ background: item.avatarColor }}
                      >
                        {item.speaker[0]}
                      </div>
                      <span style={{ color: 'var(--text-primary)' }}>{item.speaker}</span>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        ({item.role})
                      </span>
                    </div>
                    <span className="speaker-time">{item.time}</span>
                  </div>
                  <p className="transcript-text">{item.text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Interactive Action Items, Key Topics, Sentiment */}
        <div className="dashboard-sidebar-column">
          {/* Action Items Widget */}
          <div className="widget-card">
            <div className="widget-header">
              <h3 className="widget-title">
                <span>📋 Action Items</span>
                <span className="badge-count">
                  {actionItems.filter((i) => !i.completed).length} open
                </span>
              </h3>
            </div>

            <div className="action-items-interactive">
              {actionItems.map((item) => (
                <div
                  key={item.id}
                  className={`interactive-action-item ${item.completed ? 'completed' : ''}`}
                  onClick={() => toggleActionItem(item.id)}
                >
                  <input
                    type="checkbox"
                    checked={item.completed}
                    onChange={() => {}}
                    className="custom-checkbox"
                    style={{ marginTop: '2px' }}
                  />
                  <div className="action-content">
                    <span className="action-title">{item.title}</span>
                    <div className="action-meta">
                      <span className="assignee-tag">👤 {item.assignee}</span>
                      <span>⏰ {item.dueDate}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Key Topics Cloud */}
          <div className="widget-card">
            <div className="widget-header">
              <h3 className="widget-title">
                <span>🏷️ Key Topics & Tags</span>
              </h3>
            </div>

            <div className="topic-tags-cloud">
              <span className="topic-tag">⚡ FastAPI</span>
              <span className="topic-tag">🤖 Whisper STT</span>
              <span className="topic-tag">⚛️ React 19 Frontend</span>
              <span className="topic-tag">🐳 Docker Containers</span>
              <span className="topic-tag">🔄 Jenkins CI/CD</span>
              <span className="topic-tag">🔒 JWT Authentication</span>
              <span className="topic-tag">📊 pyannote.audio</span>
            </div>
          </div>

          {/* Sentiment & Engagement Meter */}
          <div className="widget-card">
            <div className="widget-header">
              <h3 className="widget-title">
                <span>📈 Meeting Sentiment</span>
              </h3>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Alignment & Productivity</span>
                <span style={{ color: 'var(--accent-emerald)', fontWeight: 700 }}>92% Positive</span>
              </div>
              <div style={{ height: '8px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: '92%', height: '100%', background: 'linear-gradient(90deg, var(--accent-cyan), var(--accent-emerald))', borderRadius: '4px' }} />
              </div>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                High consensus reached on frontend demo navigation & backend architecture.
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Presentation Demo Footer for Switching Between Screens */}
      <footer className="demo-presentation-footer">
        <div className="footer-nav-prompt">
          <span>💡 <strong>Demo Presentation Switcher:</strong> Easily jump between auth screens and this dashboard anytime.</span>
        </div>

        <div className="footer-nav-actions">
          <button
            type="button"
            className="btn-outline-nav"
            onClick={onNavigateLogin}
            id="btn-footer-goto-login"
          >
            🔐 Go to Sign In Page
          </button>
          <button
            type="button"
            className="btn-outline-nav"
            onClick={onNavigateRegister}
            id="btn-footer-goto-register"
          >
            📝 Go to Sign Up Page
          </button>
        </div>
      </footer>
    </div>
  );
};
