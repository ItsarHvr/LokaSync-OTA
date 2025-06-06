import { useState } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import {
  updateProfile,
  updatePassword,
  updateEmail,
  reauthenticateWithCredential,
  EmailAuthProvider,
  deleteUser,
  signOut,
} from "firebase/auth";
import { useNavigate } from "react-router-dom";
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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { auth } from "@/utils/firebase";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import Main from "@/components/layout/Main";
import {
  Loader2,
  Eye,
  EyeOff,
  LogOut,
  Trash2,
  User,
  Mail,
  Key,
} from "lucide-react";
import { usePageTitle } from "@/hooks/usePageTitle";
import { validatePassword, validateEmail } from "@/utils/validator";
import { toast } from "@/utils/notifications";
import { ScrollToTop } from "@/components/ui/scroll-to-top";
import Squares from "@/components/background/Squares";

export default function Profile() {
  const [user] = useAuthState(auth);
  const navigate = useNavigate();
  // Remove this line: const { toast } = useToast();

  // Form states
  const [displayName, setDisplayName] = useState(user?.displayName || "");
  const [email, setEmail] = useState(user?.email || "");

  // Separate password states for email and password forms
  const [emailCurrentPassword, setEmailCurrentPassword] = useState("");
  const [passwordCurrentPassword, setPasswordCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // UI states
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
  const [isUpdatingEmail, setIsUpdatingEmail] = useState(false);
  const [isUpdatingPassword, setIsUpdatingPassword] = useState(false);

  // Separate password visibility states
  const [showEmailPassword, setShowEmailPassword] = useState(false);
  const [showPasswordCurrent, setShowPasswordCurrent] = useState(false);
  const [showPasswordNew, setShowPasswordNew] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

  // Dialog states
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showLogoutDialog, setShowLogoutDialog] = useState(false);
  const [deletePassword, setDeletePassword] = useState("");
  const [isDeletingAccount, setIsDeletingAccount] = useState(false);

  usePageTitle("Profile Settings");

  // Get user initials for avatar
  const getUserInitials = () => {
    if (user?.displayName) {
      return user.displayName
        .split(" ")
        .map((name) => name[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    }
    if (user?.email) {
      return user.email[0].toUpperCase();
    }
    return "U";
  };

  // Reauthenticate user for sensitive operations
  const reauthenticate = async (password: string) => {
    if (!user?.email) throw new Error("No user email found");

    const credential = EmailAuthProvider.credential(user.email, password);
    await reauthenticateWithCredential(user, credential);
  };

  // Update profile (display name)
  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    const trimmedDisplayName = displayName.trim();

    // Check if display name is different from current
    if (trimmedDisplayName === (user.displayName || "")) {
      toast.warning("No changes detected", {
        description: "The display name is the same as your current name",
      });
      return;
    }

    // Validate display name length
    if (trimmedDisplayName.length < 2) {
      toast.error("Validation error", {
        description: "Display name must be at least 2 characters long",
      });
      return;
    }

    setIsUpdatingProfile(true);
    try {
      await updateProfile(user, { displayName: trimmedDisplayName });

      // SUCCESS NOTIFICATION
      toast.success("Change profile name success!", {
        description: `Your profile name has been updated to "${trimmedDisplayName}"`,
      });
    } catch (error: unknown) {
      toast.error("Failed to update profile", {
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
      });
    } finally {
      setIsUpdatingProfile(false);
    }
  };

  // Update email
  const handleUpdateEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !emailCurrentPassword) return;

    const trimmedEmail = email.trim();

    // Validate email format
    if (!validateEmail(trimmedEmail)) {
      toast.error("Validation Error", {
        description: "Please enter a valid email address",
      });
      return;
    }

    // Check if email is different from current
    if (trimmedEmail === user.email) {
      toast.error("No Changes", {
        description: "The new email is the same as your current email",
      });
      return;
    }

    setIsUpdatingEmail(true);
    try {
      // Reauthenticate first
      await reauthenticate(emailCurrentPassword);

      // Update email
      await updateEmail(user, trimmedEmail);

      toast.success("Email Updated Successfully! 📧", {
        description:
          "Your email has been changed. You'll be redirected to login.",
      });

      // Clear form
      setEmailCurrentPassword("");

      // Sign out and redirect to login after a short delay
      setTimeout(async () => {
        try {
          await signOut(auth);
          navigate("/login", { replace: true });
        } catch (error) {
          console.error("Failed to sign out after email change:", error);
          navigate("/login", { replace: true });
        }
      }, 2000);
    } catch (error: unknown) {
      toast.error("Error", {
        description:
          error instanceof Error ? error.message : "Failed to update email",
      });
    } finally {
      setIsUpdatingEmail(false);
    }
  };

  // Update password
  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !passwordCurrentPassword || !newPassword) return;

    // Validate password match
    if (newPassword !== confirmPassword) {
      toast.error("Validation Error", {
        description: "New passwords do not match",
      });
      return;
    }

    // Use the same password validation as registration
    if (!validatePassword(newPassword)) {
      toast.error("Validation Error", {
        description:
          "Password must be at least 8 characters with uppercase, lowercase, number, and special character",
      });
      return;
    }

    // Check if new password is different from current
    if (newPassword === passwordCurrentPassword) {
      toast.error("No Changes", {
        description:
          "The new password must be different from your current password",
      });
      return;
    }

    setIsUpdatingPassword(true);
    try {
      // Reauthenticate first
      await reauthenticate(passwordCurrentPassword);

      // Update password
      await updatePassword(user, newPassword);

      toast.success("Password Updated Successfully! 🔐", {
        description:
          "Your password has been changed. You'll be redirected to login for security.",
      });

      // Clear password form
      setPasswordCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");

      // Sign out and redirect to login after a short delay
      setTimeout(async () => {
        try {
          await signOut(auth);
          navigate("/login", { replace: true });
        } catch (error) {
          console.error("Failed to sign out after password change:", error);
          navigate("/login", { replace: true });
        }
      }, 2000);
    } catch (error: unknown) {
      toast.error("Error", {
        description:
          error instanceof Error ? error.message : "Failed to update password",
      });
    } finally {
      setIsUpdatingPassword(false);
    }
  };

  // Logout
  const handleLogout = async () => {
    try {
      await signOut(auth);
      toast.success("Signed Out Successfully", {
        description: "You have been logged out of your account.",
      });
      navigate("/login", { replace: true });
    } catch (error: unknown) {
      console.error("Failed to sign out", error);
      toast.error("Error", {
        description: "Failed to sign out",
      });
    }
  };

  // Delete account
  const handleDeleteAccount = async () => {
    if (!user || !deletePassword) return;

    setIsDeletingAccount(true);
    try {
      // Reauthenticate first
      await reauthenticate(deletePassword);

      // Delete user account
      await deleteUser(user);

      toast.success("Account Deleted", {
        description: "Your account has been permanently deleted.",
      });

      // Navigate to login page
      navigate("/login", { replace: true });
    } catch (error: unknown) {
      toast.error("Error", {
        description:
          error instanceof Error ? error.message : "Failed to delete account",
      });
    } finally {
      setIsDeletingAccount(false);
      setShowDeleteDialog(false);
      setDeletePassword("");
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background relative">
      {/* Squares Background Animation */}
      <div className="absolute inset-0 z-0">
        <Squares
          speed={0.2}
          squareSize={12}
          direction="diagonal"
          borderColor="#24371f"
          hoverFillColor="#284e13"
        />
      </div>

      {/* Content Layer */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <Header />
        <Main>
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
              <Avatar className="h-16 w-16">
                <AvatarImage
                  src={user?.photoURL || undefined}
                  alt={user?.displayName || user?.email || "User"}
                />
                <AvatarFallback className="text-lg font-medium">
                  {getUserInitials()}
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-3xl font-bold">Profile Settings</h1>
                <p className="text-muted-foreground">
                  Manage your account information and security settings
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column - Account Information */}
              <div className="lg:col-span-2 space-y-6">
                {/* Profile Information */}
                <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="h-5 w-5" />
                      Profile Information
                    </CardTitle>
                    <CardDescription>
                      Update your basic profile details
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleUpdateProfile} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="displayName">Display Name</Label>
                        <Input
                          id="displayName"
                          type="text"
                          placeholder="Enter your display name"
                          value={displayName}
                          onChange={(e) => setDisplayName(e.target.value)}
                          maxLength={50}
                        />
                        <p className="text-xs text-muted-foreground">
                          Must be between 2 and 50 characters
                        </p>
                      </div>

                      <Button type="submit" disabled={isUpdatingProfile}>
                        {isUpdatingProfile && (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        )}
                        Update Profile
                      </Button>
                    </form>
                  </CardContent>
                </Card>

                {/* Email Settings */}
                <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Mail className="h-5 w-5" />
                      Email Settings
                    </CardTitle>
                    <CardDescription>
                      Change your email address (requires re-authentication)
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleUpdateEmail} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="email">Email Address</Label>
                        <Input
                          id="email"
                          type="email"
                          placeholder="Enter your email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="emailCurrentPassword">
                          Current Password
                        </Label>
                        <div className="relative">
                          <Input
                            id="emailCurrentPassword"
                            type={showEmailPassword ? "text" : "password"}
                            placeholder="Enter your current password"
                            value={emailCurrentPassword}
                            onChange={(e) =>
                              setEmailCurrentPassword(e.target.value)
                            }
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-full px-3"
                            onClick={() =>
                              setShowEmailPassword(!showEmailPassword)
                            }
                          >
                            {showEmailPassword ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </div>

                      <Alert>
                        <AlertDescription className="text-sm">
                          ⚠️ After changing your email, you'll be signed out and
                          need to log in again.
                        </AlertDescription>
                      </Alert>

                      <Button
                        type="submit"
                        disabled={isUpdatingEmail || !emailCurrentPassword}
                      >
                        {isUpdatingEmail && (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        )}
                        Update Email
                      </Button>
                    </form>
                  </CardContent>
                </Card>

                {/* Password Settings */}
                <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Key className="h-5 w-5" />
                      Password Settings
                    </CardTitle>
                    <CardDescription>
                      Change your account password (requires re-authentication)
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleUpdatePassword} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="currentPasswordForChange">
                          Current Password
                        </Label>
                        <div className="relative">
                          <Input
                            id="currentPasswordForChange"
                            type={showPasswordCurrent ? "text" : "password"}
                            placeholder="Enter your current password"
                            value={passwordCurrentPassword}
                            onChange={(e) =>
                              setPasswordCurrentPassword(e.target.value)
                            }
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-full px-3"
                            onClick={() =>
                              setShowPasswordCurrent(!showPasswordCurrent)
                            }
                          >
                            {showPasswordCurrent ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="newPassword">New Password</Label>
                        <div className="relative">
                          <Input
                            id="newPassword"
                            type={showPasswordNew ? "text" : "password"}
                            placeholder="Enter your new password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-full px-3"
                            onClick={() => setShowPasswordNew(!showPasswordNew)}
                          >
                            {showPasswordNew ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Must be at least 8 characters with uppercase,
                          lowercase, number, and special character
                        </p>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="confirmPassword">
                          Confirm New Password
                        </Label>
                        <div className="relative">
                          <Input
                            id="confirmPassword"
                            type={showPasswordConfirm ? "text" : "password"}
                            placeholder="Confirm your new password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-full px-3"
                            onClick={() =>
                              setShowPasswordConfirm(!showPasswordConfirm)
                            }
                          >
                            {showPasswordConfirm ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </div>

                      <Alert>
                        <AlertDescription className="text-sm">
                          ⚠️ After changing your password, you'll be signed out
                          and need to log in again.
                        </AlertDescription>
                      </Alert>

                      <Button
                        type="submit"
                        disabled={
                          isUpdatingPassword ||
                          !passwordCurrentPassword ||
                          !newPassword ||
                          !confirmPassword
                        }
                      >
                        {isUpdatingPassword && (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        )}
                        Update Password
                      </Button>
                    </form>
                  </CardContent>
                </Card>
              </div>

              {/* Right Column - Account Actions */}
              <div className="space-y-6">
                {/* Account Actions */}
                <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                  <CardHeader>
                    <CardTitle>Account Actions</CardTitle>
                    <CardDescription>Manage your account</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Button
                      onClick={() => setShowLogoutDialog(true)}
                      variant="outline"
                      className="w-full justify-start"
                    >
                      <LogOut className="mr-2 h-4 w-4" />
                      Sign Out
                    </Button>

                    <Separator />

                    <Button
                      onClick={() => setShowDeleteDialog(true)}
                      variant="destructive"
                      className="w-full justify-start"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete Account
                    </Button>
                  </CardContent>
                </Card>

                {/* Account Information Display */}
                <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                  <CardHeader>
                    <CardTitle>Account Information</CardTitle>
                    <CardDescription>
                      Your current account details
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label className="text-sm font-medium">Email</Label>
                      <p className="text-sm text-muted-foreground">
                        {user?.email}
                      </p>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-sm font-medium">
                        Account Created
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        {user?.metadata.creationTime
                          ? new Date(
                              user.metadata.creationTime,
                            ).toLocaleDateString()
                          : "Unknown"}
                      </p>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-sm font-medium">
                        Last Sign In
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        {user?.metadata.lastSignInTime
                          ? new Date(
                              user.metadata.lastSignInTime,
                            ).toLocaleDateString()
                          : "Unknown"}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </Main>
        <Footer />

        {/* Scroll to Top Button */}
        <ScrollToTop />

        {/* Logout Confirmation Dialog */}
        <AlertDialog open={showLogoutDialog} onOpenChange={setShowLogoutDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Sign Out</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to sign out of your account?
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleLogout}>
                Sign Out
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        {/* Delete Account Confirmation Dialog */}
        <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Account</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete your
                account and remove all your data.
              </AlertDialogDescription>
            </AlertDialogHeader>

            <div className="space-y-4">
              <Alert variant="destructive">
                <AlertDescription>
                  Please enter your current password to confirm account
                  deletion.
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <Label htmlFor="deletePassword">Current Password</Label>
                <Input
                  id="deletePassword"
                  type="password"
                  placeholder="Enter your password"
                  value={deletePassword}
                  onChange={(e) => setDeletePassword(e.target.value)}
                />
              </div>
            </div>

            <AlertDialogFooter>
              <AlertDialogCancel
                onClick={() => {
                  setDeletePassword("");
                  setShowDeleteDialog(false);
                }}
              >
                Cancel
              </AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDeleteAccount}
                disabled={!deletePassword || isDeletingAccount}
                className="bg-red-600 hover:bg-red-700"
              >
                {isDeletingAccount && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Delete Account
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}
