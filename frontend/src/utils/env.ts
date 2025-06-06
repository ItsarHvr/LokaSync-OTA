export interface EnvironmentConfig {
  // Firebase Configuration
  VITE_FIREBASE_API_KEY: string;
  VITE_FIREBASE_AUTH_DOMAIN: string;
  VITE_FIREBASE_PROJECT_ID: string;
  VITE_FIREBASE_STORAGE_BUCKET: string;
  VITE_FIREBASE_MESSAGING_SENDER_ID: string;
  VITE_FIREBASE_APP_ID: string;

  // API Configuration
  VITE_API_BASE_URL: string;
  VITE_API_VERSION?: string;

  // MQTT Configuration
  VITE_MQTT_BROKER_URL: string;
  VITE_MQTT_USERNAME?: string;
  VITE_MQTT_PASSWORD?: string;
  VITE_MQTT_PUB_TOPIC?: string;
  VITE_MQTT_SUB_TOPIC_LOG?: string;
  VITE_MQTT_SUB_TOPIC_MONITORING?: string;

  // Application Configuration
  VITE_MAX_FILE_SIZE_MB?: string;
  VITE_RTO_MINUTES: string;
}

export class EnvironmentError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "EnvironmentError";
  }
}

/**
 * Helper function to validate URL format
 */
function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Helper function to validate numeric strings
 */
function isValidNumber(value: string): boolean {
  const num = Number(value);
  return !isNaN(num) && isFinite(num) && num > 0;
}

/**
 * Validates that all required environment variables are present and properly formatted
 * This is the main function - only used for validation before app starts
 * @throws {EnvironmentError} When required environment variables are missing or invalid
 */
export const validateEnv = (): void => {
  // Required environment variables
  const required = [
    "VITE_FIREBASE_API_KEY",
    "VITE_FIREBASE_AUTH_DOMAIN",
    "VITE_FIREBASE_PROJECT_ID",
    "VITE_FIREBASE_STORAGE_BUCKET",
    "VITE_FIREBASE_MESSAGING_SENDER_ID",
    "VITE_FIREBASE_APP_ID",
    "VITE_API_BASE_URL",
    "VITE_MQTT_BROKER_URL",
    "VITE_RTO_MINUTES",
  ] as const;

  // Check for missing required variables
  const missing = required.filter((key) => !import.meta.env[key]);
  if (missing.length > 0) {
    throw new EnvironmentError(
      `Missing required environment variables: ${missing.join(", ")}\n\n` +
        "Please check your .env file and ensure all required variables are set.",
    );
  }

  // Validate environment variable formats
  const env = import.meta.env;
  const errors: string[] = [];

  // Validate Firebase API Key format
  if (
    env.VITE_FIREBASE_API_KEY &&
    !/^[A-Za-z0-9_-]+$/.test(env.VITE_FIREBASE_API_KEY)
  ) {
    errors.push(
      "VITE_FIREBASE_API_KEY: Invalid format (must contain only letters, numbers, underscores, and hyphens)",
    );
  }

  // Validate URLs
  const urlValidations = [
    {
      field: "VITE_API_BASE_URL",
      value: env.VITE_API_BASE_URL,
      expectedProtocols: ["http:", "https:"],
      description: "API base URL",
    },
    {
      field: "VITE_MQTT_BROKER_URL",
      value: env.VITE_MQTT_BROKER_URL,
      expectedProtocols: ["ws:", "wss:"],
      description: "MQTT broker URL",
    },
  ];

  urlValidations.forEach(({ field, value, expectedProtocols, description }) => {
    if (value) {
      // First check if it's a valid URL format
      if (!isValidUrl(value)) {
        errors.push(
          `${field}: Invalid URL format for ${description}\n` +
            `Expected format: ${expectedProtocols[0]}//example.com`,
        );
        return;
      }

      // Then check the protocol
      try {
        const parsedUrl = new URL(value);
        if (!expectedProtocols.includes(parsedUrl.protocol)) {
          errors.push(
            `${field}: Invalid protocol for ${description}. Expected ${expectedProtocols.join(" or ")}, got ${parsedUrl.protocol}\n` +
              `Example: ${expectedProtocols[0]}//example.com`,
          );
        }
      } catch {
        errors.push(
          `${field}: Invalid URL format for ${description}\n` +
            `Expected format: ${expectedProtocols[0]}//example.com`,
        );
      }
    }
  });

  // Validate numeric values
  if (env.VITE_RTO_MINUTES && !isValidNumber(env.VITE_RTO_MINUTES)) {
    errors.push("VITE_RTO_MINUTES: Must be a valid positive number");
  }

  if (env.VITE_MAX_FILE_SIZE_MB && !isValidNumber(env.VITE_MAX_FILE_SIZE_MB)) {
    errors.push("VITE_MAX_FILE_SIZE_MB: Must be a valid positive number");
  }

  // Validate Firebase Project ID format
  if (
    env.VITE_FIREBASE_PROJECT_ID &&
    !/^[a-z0-9-]+$/.test(env.VITE_FIREBASE_PROJECT_ID)
  ) {
    errors.push(
      "VITE_FIREBASE_PROJECT_ID: Invalid format (must contain only lowercase letters, numbers, and hyphens)",
    );
  }

  // Throw error if any validation failed
  if (errors.length > 0) {
    throw new EnvironmentError(
      `Environment validation failed:\n\n${errors.map((err) => `• ${err}`).join("\n\n")}`,
    );
  }
};
