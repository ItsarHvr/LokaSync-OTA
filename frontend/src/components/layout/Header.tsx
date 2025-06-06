import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { signOut } from "firebase/auth";
import { useAuthState } from "react-firebase-hooks/auth";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { auth } from "@/utils/firebase";
import { Menu, X, ChevronDown } from "lucide-react";

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [user] = useAuthState(auth);
  const location = useLocation();

  useEffect(() => {
    setIsMenuOpen(false);
    setIsProfileMenuOpen(false);
  }, [location]);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const toggleProfileMenu = () => {
    setIsProfileMenuOpen(!isProfileMenuOpen);
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error("Failed to log out", error);
    }
  };

  // Get user initials for avatar fallback
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

  const isAuthPage = ["/login", "/register", "/forgot-password"].includes(
    location.pathname,
  );
  if (isAuthPage) return null;

  return (
    <header className="bg-background border-b border-border shadow-sm sticky top-0 z-50 w-full">
      <div className="w-full px-3 sm:px-4 lg:px-6">
        <nav className="flex items-center justify-between h-14 max-w-7xl mx-auto">
          {/* Logo */}
          <div className="flex items-center">
            <Link
              to="/dashboard"
              className="flex items-center text-primary font-bold text-lg sm:text-xl"
            >
              <img
                src="/lokasync_logo.png"
                alt="LokaSync Logo"
                className="h-6 w-6 sm:h-8 sm:w-8 mr-2"
              />
              LokaSync
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            <Link
              to="/dashboard"
              className={`px-3 py-2 rounded text-sm transition-colors duration-150 ${
                location.pathname.includes("/dashboard")
                  ? "text-primary font-medium bg-accent"
                  : "text-muted-foreground hover:text-primary"
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/log"
              className={`px-3 py-2 rounded text-sm transition-colors duration-150 ${
                location.pathname.includes("/log")
                  ? "text-primary font-medium bg-accent"
                  : "text-muted-foreground hover:text-primary"
              }`}
            >
              Log Update
            </Link>
            <Link
              to="/monitoring"
              className={`px-3 py-2 rounded text-sm transition-colors duration-150 ${
                location.pathname.includes("/monitoring")
                  ? "text-primary font-medium bg-accent"
                  : "text-muted-foreground hover:text-primary"
              }`}
            >
              Monitoring
            </Link>

            {/* Profile Menu with Avatar Only */}
            {user && (
              <div className="relative ml-3">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleProfileMenu}
                  className="flex items-center gap-1 text-muted-foreground hover:text-primary text-sm p-1"
                >
                  <Avatar className="h-8 w-8">
                    <AvatarImage
                      src={user.photoURL || undefined}
                      alt={user.displayName || user.email || "User"}
                    />
                    <AvatarFallback className="text-xs font-medium">
                      {getUserInitials()}
                    </AvatarFallback>
                  </Avatar>
                  <ChevronDown className="h-3 w-3" />
                </Button>

                {isProfileMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-background rounded-md shadow-lg py-1 z-10 border border-border">
                    <div className="px-3 py-2 border-b border-border">
                      <p className="text-sm font-medium text-foreground truncate">
                        {user.displayName || "User"}
                      </p>
                      <p className="text-xs text-muted-foreground truncate">
                        {user.email}
                      </p>
                    </div>
                    <Link
                      to="/profile"
                      className="block px-3 py-2 text-sm text-foreground hover:bg-accent"
                    >
                      Profile Settings
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-3 py-2 text-sm text-foreground hover:bg-accent"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button variant="ghost" size="sm" onClick={toggleMenu}>
              {isMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>
          </div>
        </nav>

        {/* Mobile Navigation Links */}
        {isMenuOpen && (
          <div className="md:hidden bg-background py-2 border-t border-border max-w-7xl mx-auto">
            <Link
              to="/dashboard"
              className={`block px-3 py-2 rounded text-sm ${
                location.pathname.includes("/dashboard")
                  ? "text-primary font-medium bg-accent"
                  : "text-muted-foreground"
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/log"
              className={`block px-3 py-2 rounded text-sm ${
                location.pathname.includes("/log")
                  ? "text-primary font-medium bg-accent"
                  : "text-muted-foreground"
              }`}
            >
              Log Update
            </Link>
            <Link
              to="/monitoring"
              className={`block px-3 py-2 rounded text-sm ${
                location.pathname.includes("/monitoring")
                  ? "text-primary font-medium bg-accent"
                  : "text-muted-foreground"
              }`}
            >
              Monitoring
            </Link>

            {user && (
              <>
                <div className="px-3 py-2 border-t border-border mt-2">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10">
                      <AvatarImage
                        src={user.photoURL || undefined}
                        alt={user.displayName || user.email || "User"}
                      />
                      <AvatarFallback className="text-sm font-medium">
                        {getUserInitials()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex flex-col min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">
                        {user.displayName || "User"}
                      </p>
                      <p className="text-xs text-muted-foreground truncate">
                        {user.email}
                      </p>
                    </div>
                  </div>
                </div>
                <Link
                  to="/profile"
                  className="block px-3 py-2 text-sm text-muted-foreground hover:text-primary"
                >
                  Profile Settings
                </Link>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-3 py-2 text-sm text-muted-foreground hover:text-primary"
                >
                  Sign Out
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
