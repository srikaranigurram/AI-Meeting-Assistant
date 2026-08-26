import React from 'react';

export const BrandHero = () => {
  return (
    <div className="brand-hero">
      {/* Top Branding */}
      <div>
        <div className="brand-header">
          <div className="brand-logo-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" x2="12" y1="19" y2="22"/>
              <line x1="8" x2="16" y1="22" y2="22"/>
            </svg>
          </div>
          <h1 className="brand-title">AI Meeting Assistant</h1>
        </div>

        <div className="brand-badge">
          <span className="brand-badge-dot"></span>
          Intelligent Meeting Automation
        </div>

        <h2 className="brand-headline">
          Turn your conversations into <span>actionable intelligence.</span>
        </h2>

        <p className="brand-description">
          Record, transcribe, and summarize your meetings automatically. 
          Extract actionable tasks, detect key decisions, and sync deadlines effortlessly.
        </p>

        {/* Live Audio Visualizer Demonstration */}
        <div className="audio-preview-card">
          <div className="audio-preview-header">
            <span className="audio-live-pill">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10"/>
              </svg>
              Live Audio Processing
            </span>
            <span>Whisper AI • Active</span>
          </div>

          <div className="wave-bars" aria-hidden="true">
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
          </div>

          <div className="transcript-sample">
            <span className="transcript-speaker">AI Agent:</span>
            "Action item identified: Sarah to finalize Q3 deployment pipeline by Friday."
          </div>
        </div>
      </div>

      {/* Feature Pills */}
      <div className="feature-list">
        <div className="feature-item">
          <div className="feature-icon-wrapper">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </div>
          <span>Speech-to-text transcription with 99% accuracy</span>
        </div>

        <div className="feature-item">
          <div className="feature-icon-wrapper">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </div>
          <span>Automatic summary & task assignment</span>
        </div>

        <div className="feature-item">
          <div className="feature-icon-wrapper">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </div>
          <span>DevOps ready: Dockerized and CI/CD integrated</span>
        </div>
      </div>
    </div>
  );
};
