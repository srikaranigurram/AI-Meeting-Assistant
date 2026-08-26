import React from 'react';

export const PasswordStrengthMeter = ({ validationResult, showDetails = true }) => {
  if (!validationResult) return null;

  const { score, label, checks } = validationResult;

  const getStrengthClass = (lvl) => {
    switch (lvl) {
      case 'Weak': return 'strength-weak';
      case 'Fair': return 'strength-fair';
      case 'Good': return 'strength-good';
      case 'Strong': return 'strength-strong';
      default: return '';
    }
  };

  return (
    <div className="strength-meter-container">
      <div className="strength-bars">
        <div className={`strength-bar-segment ${score >= 1 ? getStrengthClass(label) : ''}`} />
        <div className={`strength-bar-segment ${score >= 2 ? getStrengthClass(label) : ''}`} />
        <div className={`strength-bar-segment ${score >= 3 ? getStrengthClass(label) : ''}`} />
        <div className={`strength-bar-segment ${score >= 4 ? getStrengthClass(label) : ''}`} />
      </div>

      <div className="strength-label-row">
        <span>Password strength:</span>
        <span className={`strength-text ${getStrengthClass(label)}`}>
          {label}
        </span>
      </div>

      {showDetails && checks && (
        <div className="password-checklist">
          <div className={`check-item ${checks.minLength ? 'passed' : ''}`}>
            <span>{checks.minLength ? '✓' : '○'}</span>
            <span>At least 8 characters</span>
          </div>
          <div className={`check-item ${checks.hasUpper && checks.hasLower ? 'passed' : ''}`}>
            <span>{checks.hasUpper && checks.hasLower ? '✓' : '○'}</span>
            <span>Upper & lowercase</span>
          </div>
          <div className={`check-item ${checks.hasNumber ? 'passed' : ''}`}>
            <span>{checks.hasNumber ? '✓' : '○'}</span>
            <span>At least 1 number</span>
          </div>
          <div className={`check-item ${checks.hasSpecial ? 'passed' : ''}`}>
            <span>{checks.hasSpecial ? '✓' : '○'}</span>
            <span>1 special symbol</span>
          </div>
        </div>
      )}
    </div>
  );
};
