import { auth } from "@/utils/firebase";

/**
 * Get the current user's ID token
 */
export const getAuthToken = async (): Promise<string | null> => {
  try {
    const user = auth.currentUser;
    if (!user) {
      return null;
    }

    const token = await user.getIdToken();
    return token;
  } catch (error) {
    console.error("Failed to get auth token:", error);
    return null;
  }
};

/**
 * Get the current user's ID token (force refresh)
 */
export const getAuthTokenRefresh = async (): Promise<string | null> => {
  try {
    const user = auth.currentUser;
    if (!user) {
      return null;
    }

    const token = await user.getIdToken(true); // Force refresh
    return token;
  } catch (error) {
    console.error("Failed to refresh auth token:", error);
    return null;
  }
};
