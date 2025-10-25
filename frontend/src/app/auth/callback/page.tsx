import { createSupabaseServerClient } from "@/integrations/supabase/server";
import { Loader2 } from "lucide-react";
import { redirect } from "next/navigation";
import { Suspense } from "react";

async function AuthCallbackHandler({ code }: { code: string | null }) {
  if (code) {
    const supabase = createSupabaseServerClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (error) {
      console.error("Auth callback error:", error.message);
      redirect(`/login?error=${encodeURIComponent(error.message)}`);
    } else {
      redirect("/onboarding");
    }
  }

  redirect("/login?error=Invalid_callback_request");

  return null;
}

export default function AuthCallbackPage({
  searchParams,
}: {
  searchParams: { code?: string; error?: string; error_description?: string };
}) {
  const { code, error, error_description } = searchParams;

  if (error) {
    console.error("OAuth Error:", error, error_description);
    redirect(
      `/login?error=${encodeURIComponent(
        error_description || "An error occurred during authentication."
      )}`
    );
  }

  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted p-6">
      <Suspense
        fallback={
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
            <div className="text-center">
              <h1 className="text-xl font-semibold">
                Connecting your account...
              </h1>
              <p className="mt-2 text-sm text-muted-foreground">
                Just a moment while we set things up
              </p>
            </div>
          </div>
        }
      >
        <AuthCallbackHandler code={code || null} />
      </Suspense>
    </div>
  );
}

