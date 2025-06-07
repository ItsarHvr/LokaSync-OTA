import { useState } from "react";
import { Link } from "react-router-dom";
import { sendPasswordResetEmail } from "firebase/auth";
import { ArrowLeft, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import Squares from "@/components/background/Squares";
import { auth } from "@/utils/firebase";
import {
  sanitizeInput,
  validateResetPasswordForm,
  getFirebaseErrorMessage,
} from "@/utils/validator";
import { usePageTitle } from "@/hooks/usePageTitle";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isEmailSent, setIsEmailSent] = useState(false);

  usePageTitle("Forgot Password");

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setMessage("");

    const sanitizedEmail = sanitizeInput(email);
    const validationError = validateResetPasswordForm(sanitizedEmail);

    if (validationError) {
      setError(validationError);
      setIsLoading(false);
      return;
    }

    try {
      await sendPasswordResetEmail(auth, sanitizedEmail);
      setMessage("Password reset email sent! Check your inbox.");
      setIsEmailSent(true);
    } catch (error: unknown) {
      setError(getFirebaseErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  const handleTryAgain = () => {
    setIsEmailSent(false);
    setMessage("");
    setError("");
    setEmail("");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-3 sm:p-4 relative overflow-hidden">
      {/* Squares Background Animation */}
      <div className="absolute inset-0 z-0">
        <Squares
          speed={0.5}
          squareSize={15}
          direction="diagonal"
          borderColor="#24371f"
          hoverFillColor="#284e13"
        />
      </div>

      {/* Forgot Password Card */}
      <Card className="w-full max-w-sm sm:max-w-md mx-auto relative z-10 backdrop-blur-sm bg-card/95 border-border/50 shadow-2xl">
        <CardHeader className="text-center pb-4">
          <div className="mx-auto mb-3 flex h-16 w-16 sm:h-20 sm:w-20 items-center justify-center">
            <img
              src="/lokasync_logo.png"
              alt="LokaSync Logo"
              className="h-full w-full object-contain"
            />
          </div>
          <CardTitle className="text-xl sm:text-2xl font-bold">
            {isEmailSent ? "Check your email" : "Reset password"}
          </CardTitle>
          <CardDescription className="text-sm">
            {isEmailSent
              ? "We've sent a password reset link to your email address."
              : "Enter your email address and we'll send you a link to reset your password."}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {!isEmailSent ? (
            <form onSubmit={handleResetPassword} className="space-y-3">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription className="text-sm">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              <div className="space-y-1.5">
                <Label htmlFor="email" className="text-sm">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value.trim())}
                  required
                  autoFocus
                  autoComplete="email"
                  className="h-9"
                />
              </div>

              <Button
                type="submit"
                className="w-full h-9 mt-4"
                disabled={isLoading}
              >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Send Reset Link
              </Button>

              <div className="text-center pt-2">
                <Link
                  to="/login"
                  className="inline-flex items-center text-xs sm:text-sm text-primary hover:underline"
                >
                  <ArrowLeft className="mr-1 h-3 w-3" />
                  Back to sign in
                </Link>
              </div>
            </form>
          ) : (
            <div className="space-y-3">
              {message && (
                <Alert>
                  <AlertDescription className="text-sm">
                    {message}
                  </AlertDescription>
                </Alert>
              )}

              <div className="text-center space-y-3">
                <p className="text-xs sm:text-sm text-muted-foreground">
                  Didn't receive the email? Check your spam folder or try again.
                </p>
                <Button
                  variant="outline"
                  className="h-9"
                  onClick={handleTryAgain}
                >
                  Try Again
                </Button>
              </div>

              <div className="text-center pt-2">
                <Link
                  to="/login"
                  className="inline-flex items-center text-xs sm:text-sm text-primary hover:underline"
                >
                  <ArrowLeft className="mr-1 h-3 w-3" />
                  Back to sign in
                </Link>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
