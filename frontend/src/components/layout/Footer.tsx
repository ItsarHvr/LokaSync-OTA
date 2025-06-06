import { useLocation } from "react-router-dom";

const Footer = () => {
  const location = useLocation();

  // Determine if we should show the footer (not on auth pages)
  const isAuthPage = ["/login", "/register", "/forgot-password"].includes(
    location.pathname,
  );
  if (isAuthPage) return null;

  return (
    <footer className="bg-background border-t border-border py-4 mt-auto w-full">
      <div className="w-full px-3 sm:px-4 lg:px-6">
        <div className="flex flex-col sm:flex-row justify-between items-center max-w-7xl mx-auto">
          <div className="mb-2 sm:mb-0">
            <p className="text-xs sm:text-sm text-muted-foreground">
              &copy; {new Date().getFullYear()} LokaSync - All rights reserved.
            </p>
          </div>

          <div className="flex space-x-3 sm:space-x-4">
            <a
              href="https://github.com/LokaSync/LokaSync"
              target="_blank"
              className="text-xs sm:text-sm text-muted-foreground hover:text-primary"
            >
              LokaSync Repo
            </a>
            <a
              href="https://lokatani.id/contact-us"
              target="_blank"
              className="text-xs sm:text-sm text-muted-foreground hover:text-primary"
            >
              Contact Lokatani
            </a>
            <a
              href="mailto:itsar.hevara.tik22@mhsw.pnj.ac.id"
              className="text-xs sm:text-sm text-muted-foreground hover:text-primary"
            >
              Contact Us
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
