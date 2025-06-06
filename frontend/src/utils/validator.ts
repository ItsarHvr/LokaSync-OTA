import { FirebaseError } from "firebase/app";

// Input sanitization
export const sanitizeInput = (input: string): string => {
  return input.trim().replace(/[<>\\"'&]/g, "");
};

// Email validation
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Name validation
export const validateName = (name: string): boolean => {
  const nameRegex = /^[a-zA-Z\s]{2,50}$/;
  return nameRegex.test(name);
};

// Password validation
export const validatePassword = (password: string): boolean => {
  // At least 8 characters with uppercase, lowercase, number, and special character
  // Expanded special characters: @$!%*?&^#()[]{}|;:,.<>_+-=~`"'
  const passwordRegex =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&^#()[\]{}|;:,.<>_+\-=~`"'])[A-Za-z\d@$!%*?&^#()[\]{}|;:,.<>_+\-=~`"']{8,}$/;
  return passwordRegex.test(password);
};

// Firebase error handling
export const getFirebaseErrorMessage = (error: unknown): string => {
  if (error instanceof FirebaseError) {
    switch (error.code) {
      case "auth/invalid-credential":
        return "Invalid email or password";
      case "auth/user-not-found":
        return "No account found with this email";
      case "auth/wrong-password":
        return "Invalid email or password";
      case "auth/invalid-email":
        return "Invalid email address";
      case "auth/email-already-in-use":
        return "An account with this email already exists";
      case "auth/weak-password":
        return "Password is too weak. Please choose a stronger password";
      case "auth/too-many-requests":
        return "Too many failed attempts. Please try again later";
      case "auth/user-disabled":
        return "This account has been disabled";
      case "auth/operation-not-allowed":
        return "This operation is not allowed";
      case "auth/invalid-action-code":
        return "Invalid or expired reset code";
      case "auth/expired-action-code":
        return "Reset code has expired";
      default:
        return "An error occurred. Please try again";
    }
  }

  if (error instanceof Error) {
    return error.message || "An error occurred. Please try again";
  }

  return "An unexpected error occurred. Please try again";
};

// Form validation functions
export interface LoginValidation {
  email: string;
  password: string;
}

export interface RegisterValidation {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export const validateLoginForm = (data: LoginValidation): string | null => {
  if (!validateEmail(data.email)) {
    return "Please enter a valid email address";
  }

  if (data.password.length < 6) {
    return "Password must be at least 6 characters";
  }

  return null;
};

export const validateRegisterForm = (
  data: RegisterValidation,
): string | null => {
  if (!validateName(data.name)) {
    return "Name must be 2-50 characters and contain only letters";
  }

  if (!validateEmail(data.email)) {
    return "Please enter a valid email address";
  }

  if (!validatePassword(data.password)) {
    return "Password must be at least 8 characters with uppercase, lowercase, number, and special character";
  }

  if (data.password !== data.confirmPassword) {
    return "Passwords do not match";
  }

  return null;
};

export const validateResetPasswordForm = (email: string): string | null => {
  if (!validateEmail(email)) {
    return "Please enter a valid email address";
  }

  return null;
};
