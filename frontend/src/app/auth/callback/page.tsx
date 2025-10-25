"use client";

import { useEffect, useState, useRef, useCallback, memo } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

const ErrorIcon = memo(() => (
  <div className="rounded-full bg-destructive/10 p-3">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className="h-12 w-12 text-destructive"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M6 18L18 6M6 6l12 12"
      />
    </svg>
  </div>
));

ErrorIcon.displayName = "ErrorIcon";

export default function AuthCallbackPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const hasProcessed = useRef(false);

  const redirectToLogin = useCallback(() => {
    setTimeout(() => router.push("/login"), 3000);
  }, [router]);

  const redirectToDestination = useCallback((destination: string) => {
    router.push(destination);
  }, [router]);

  useEffect(() => {
    // Prevent double execution in development mode
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const handleCallback = async () => {
      try {
        const searchParams = new URLSearchParams(window.location.search);
        const code = searchParams.get('code');
        const errorParam = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');

        // Handle OAuth errors from provider
        if (errorParam) {
          setError(errorDescription || errorParam);
          redirectToLogin();
          return;
        }

        // Exchange code for session
        if (code) {
          const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);

          if (exchangeError) {
            console.error("Exchange error:", exchangeError);
            setError(exchangeError.message);
            redirectToLogin();
            return;
          }
        }

        // Verify authentication
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();

        if (sessionError) {
          console.error("Session error:", sessionError);
          setError("Failed to retrieve session");
          redirectToLogin();
          return;
        }

        if (session?.user) {
          // Successfully authenticated - redirect to chat
          redirectToDestination("/chat");
        } else {
          setError("No active session found");
          redirectToLogin();
        }
      } catch (err) {
        console.error("Unexpected callback error:", err);
        setError(err instanceof Error ? err.message : "An unexpected error occurred");
        redirectToLogin();
      }
    };

    handleCallback();
  }, [redirectToLogin, redirectToDestination]);

  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted p-6">
      <div className="flex flex-col items-center gap-4">
        {error ? (
          <>
            <ErrorIcon />
            <div className="text-center max-w-md">
              <h1 className="text-xl font-semibold text-destructive">
                Authentication Failed
              </h1>
              <p className="mt-2 text-sm text-muted-foreground">{error}</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Redirecting to login page...
              </p>
            </div>
          </>
        ) : (
          <>
            <Loader2 className="h-12 w-12 animate-spin text-primary" aria-label="Loading" />
            <div className="text-center max-w-md">
              <h1 className="text-xl font-semibold">Connecting your account...</h1>
              <p className="mt-2 text-sm text-muted-foreground">
                Just a moment while we set things up
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
