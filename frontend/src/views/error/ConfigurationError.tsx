import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { AlertTriangle, RefreshCw } from "lucide-react";
import Squares from "@/components/background/Squares";
import { ScrollToTop } from "@/components/ui/scroll-to-top";
import { usePageTitle } from "@/hooks/usePageTitle";

interface ConfigurationErrorProps {
  error: Error;
}

export default function ConfigurationError({ error }: ConfigurationErrorProps) {
  usePageTitle("Configuration Error");

  const handleRetry = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-3 sm:p-4 relative overflow-hidden">
      {/* Squares Background Animation */}
      <div className="absolute inset-0 z-0">
        <Squares
          speed={0.3}
          squareSize={15}
          direction="diagonal"
          borderColor="#24371f"
          hoverFillColor="#284e13"
        />
      </div>

      {/* Configuration Error Card */}
      <Card className="w-full max-w-2xl mx-auto relative z-10 backdrop-blur-sm bg-card/95 border-border/50 shadow-2xl">
        <CardHeader className="text-center pb-4">
          {/* Logo */}
          <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center">
            <img
              src="/lokasync_logo.png"
              alt="LokaSync Logo"
              className="h-full w-full object-contain"
            />
          </div>

          {/* Title with Alert Icon */}
          <div className="flex items-center justify-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
              <AlertTriangle className="h-6 w-6 text-destructive" />
            </div>
            <CardTitle className="text-2xl sm:text-3xl font-bold text-destructive">
              Configuration Error
            </CardTitle>
          </div>

          <CardDescription className="text-base">
            The application could not start due to missing or invalid
            environment configuration.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Error Details */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold">Error Details:</h3>
            <div className="bg-muted/50 border border-destructive/20 rounded-lg p-4">
              <pre className="text-sm text-foreground whitespace-pre-wrap break-words font-mono overflow-x-auto">
                {error.message}
              </pre>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={handleRetry}
              className="w-full sm:flex-1"
              size="lg"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>

          {/* Help Information */}
          <div className="bg-muted/30 border border-border rounded-lg p-4 space-y-3">
            <h4 className="font-semibold text-sm">💡 How to fix this issue:</h4>
            <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
              <li>
                Check your{" "}
                <code className="bg-muted px-1 py-0.5 rounded text-xs">
                  .env
                </code>{" "}
                file exists.
              </li>
              <li>Ensure all required environment variables are set.</li>
              <li>
                Verify URL formats are correct (
                <span className="font-semibold">http/https</span> for API,{" "}
                <span className="font-semibold">ws/wss</span> for MQTT)
              </li>
              <li>Check numeric values are valid numbers.</li>
              <li>Contact your web developer if needed.</li>
            </ul>
          </div>

          {/* Contact Information */}
          <div className="text-center pt-4 border-t border-border">
            <p className="text-sm text-muted-foreground mb-3">
              Need help? Contact support:
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <a
                href="https://lokatani.com/contact-us"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Lokatani
              </a>
              <a
                href="mailto:itsar.hevara.tik22@mhsw.pnj.ac.id"
                className="text-primary hover:underline"
              >
                LokaSync Team Lead
              </a>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Scroll to Top Button */}
      <ScrollToTop />
    </div>
  );
}
