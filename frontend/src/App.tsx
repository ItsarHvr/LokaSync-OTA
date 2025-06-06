import { useState, useEffect } from "react";
import "./App.css";
import { ThemeProvider } from "./components/theme-provider";
import AppRoutes from "./routes/AppRoutes";
import { validateEnv } from "./utils/env";
import ConfigurationError from "./views/error/ConfigurationError";

export default function App() {
  const [envValidated, setEnvValidated] = useState(false);
  const [validationError, setValidationError] = useState<Error | null>(null);

  useEffect(() => {
    try {
      validateEnv();
      setEnvValidated(true);
    } catch (error) {
      setValidationError(error as Error);
    }
  }, []);

  return (
    <ThemeProvider defaultTheme="dark" storageKey="lokasync-theme">
      {envValidated ? (
        <AppRoutes />
      ) : validationError ? (
        <ConfigurationError error={validationError} />
      ) : (
        // Loading state while validating
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Validating configuration...</p>
          </div>
        </div>
      )}
    </ThemeProvider>
  );
}
