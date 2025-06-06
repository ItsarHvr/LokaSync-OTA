import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Home, ArrowLeft } from "lucide-react";
import Squares from "@/components/background/Squares";
import { usePageTitle } from "@/hooks/usePageTitle";

export default function NotFound() {
  usePageTitle("Page Not Found");

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

      {/* 404 Card */}
      <Card className="w-full max-w-lg mx-auto relative z-10 backdrop-blur-sm bg-card/95 border-border/50 shadow-2xl">
        <CardHeader className="text-center pb-4">
          {/* Logo */}
          <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center">
            <img
              src="/lokasync_logo.png"
              alt="LokaSync Logo"
              className="h-full w-full object-contain"
            />
          </div>

          {/* 404 Number */}
          <div className="mb-4">
            <h1 className="text-6xl sm:text-7xl font-bold text-primary mb-2">
              404
            </h1>
          </div>

          <CardTitle className="text-2xl sm:text-3xl font-bold mb-2">
            Page Not Found
          </CardTitle>
          <CardDescription className="text-base">
            The page you are looking for doesn't exist or has been moved.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Link to="/dashboard" className="flex-1">
              <Button className="w-full h-10" size="lg">
                <Home className="h-4 w-4 mr-2" />
                Go to Dashboard
              </Button>
            </Link>

            <Button
              variant="outline"
              className="w-full sm:w-auto h-10"
              size="lg"
              onClick={() => window.history.back()}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Go Back
            </Button>
          </div>

          {/* Additional Help Text */}
          <div className="text-center pt-4 border-t">
            <p className="text-sm text-muted-foreground mb-3">
              Need help? Here are some useful links:
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <Link to="/dashboard" className="text-primary hover:underline">
                Dashboard
              </Link>
              <Link to="/log" className="text-primary hover:underline">
                Log Updates
              </Link>
              <Link to="/profile" className="text-primary hover:underline">
                Profile
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
