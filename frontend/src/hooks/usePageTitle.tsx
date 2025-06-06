import { useEffect } from "react";

export const usePageTitle = (title: string) => {
  useEffect(() => {
    const previousTitle = document.title;
    document.title = `LokaSync | ${title}`;

    // Cleanup function to restore previous title
    return () => {
      document.title = previousTitle;
    };
  }, [title]);
};
