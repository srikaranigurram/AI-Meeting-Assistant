/**
 * AI Meeting Assistant - Frontend Validation Utilities
 * 
 * Form validation helpers for Login, Registration, and Password Reset.
 */

// Email regex pattern (RFC 5322 compliant simplified)
export const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

/**
 * Validate an email address
 * @param {string} email 
 * @returns {{ isValid: boolean, message: string }}
 */
export function validateEmail(email) {
  if (!email || !email.trim()) {
    return { isValid: false, message: 'Email address is required.' };
  }
  const cleanEmail = email.trim();
  if (!EMAIL_REGEX.test(cleanEmail)) {
    return { isValid: false, message: 'Please enter a valid email address (e.g. name@company.com).' };
  }
  return { isValid: true, message: '' };
}

/**
 * Validate full name
 * @param {string} name 
 * @returns {{ isValid: boolean, message: string }}
 */
export function validateFullName(name) {
  if (!name || !name.trim()) {
    return { isValid: false, message: 'Full name is required.' };
  }
  const cleanName = name.trim();
  if (cleanName.length < 2) {
    return { isValid: false, message: 'Full name must be at least 2 characters long.' };
  }
  return { isValid: true, message: '' };
}

/**
 * Assess password strength and validation
 * @param {string} password 
 * @returns {{
 *   isValid: boolean,
 *   score: number, // 0 to 4
 *   label: 'Weak' | 'Fair' | 'Good' | 'Strong',
 *   checks: { minLength: boolean, hasUpper: boolean, hasLower: boolean, hasNumber: boolean, hasSpecial: boolean },
 *   message: string
 * }}
 */
export function validatePassword(password) {
  if (!password) {
    return {
      isValid: false,
      score: 0,
      label: 'Weak',
      checks: {
        minLength: false,
        hasUpper: false,
        hasLower: false,
        hasNumber: false,
        hasSpecial: false,
      },
      message: 'Password is required.',
    };
  }

  const checks = {
    minLength: password.length >= 8,
    hasUpper: /[A-Z]/.test(password),
    hasLower: /[a-z]/.test(password),
    hasNumber: /[0-9]/.test(password),
    hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(password),
  };

  let passedCount = 0;
  if (checks.minLength) passedCount++;
  if (checks.hasUpper && checks.hasLower) passedCount++;
  if (checks.hasNumber) passedCount++;
  if (checks.hasSpecial) passedCount++;

  let label = 'Weak';
  if (passedCount === 2) label = 'Fair';
  if (passedCount === 3) label = 'Good';
  if (passedCount === 4 && password.length >= 10) label = 'Strong';
  else if (passedCount === 4) label = 'Good';

  const isValid = checks.minLength && (checks.hasUpper || checks.hasLower) && checks.hasNumber;

  let message = '';
  if (!checks.minLength) {
    message = 'Password must be at least 8 characters long.';
  } else if (!isValid) {
    message = 'Password should contain letters and numbers.';
  }

  return {
    isValid,
    score: passedCount,
    label,
    checks,
    message,
  };
}

/**
 * Validate password confirmation
 * @param {string} password 
 * @param {string} confirmPassword 
 * @returns {{ isValid: boolean, message: string }}
 */
export function validateConfirmPassword(password, confirmPassword) {
  if (!confirmPassword) {
    return { isValid: false, message: 'Please confirm your password.' };
  }
  if (password !== confirmPassword) {
    return { isValid: false, message: 'Passwords do not match.' };
  }
  return { isValid: true, message: '' };
}
