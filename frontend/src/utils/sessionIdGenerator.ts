/**
 * Generate a random session ID with only alphanumeric characters
 * Format: 5 random alphanumeric characters + 5 digits
 * Example: "AbC3k12345"
 */
export const generateSessionId = (): string => {
  // Characters to use (only letters and numbers)
  const alphanumericChars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

  // Generate 5 random alphanumeric characters
  let randomPart = "";
  for (let i = 0; i < 5; i++) {
    randomPart += alphanumericChars.charAt(
      Math.floor(Math.random() * alphanumericChars.length),
    );
  }

  // Generate 5 random digits
  let numberPart = "";
  for (let i = 0; i < 5; i++) {
    numberPart += Math.floor(Math.random() * 10).toString();
  }

  return randomPart + numberPart;
};
