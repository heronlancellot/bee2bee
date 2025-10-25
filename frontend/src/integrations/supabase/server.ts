import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import type { Database } from './types';

export function createSupabaseServerClient() {

  const cookieStore = cookies();

  const USE_LOCAL = process.env.NEXT_PUBLIC_USE_LOCAL_SUPABASE === 'true';
  const LOCAL_SUPABASE_URL = "http://127.0.0.1:54321";
  const LOCAL_SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0";
  const REMOTE_SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const REMOTE_SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  const SUPABASE_URL = USE_LOCAL
    ? LOCAL_SUPABASE_URL
    : REMOTE_SUPABASE_URL;

  const SUPABASE_ANON_KEY = USE_LOCAL
    ? LOCAL_SUPABASE_ANON_KEY
    : REMOTE_SUPABASE_ANON_KEY;

  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    throw new Error(
      "Missing Supabase configuration. Check your .env.local file."
    );
  }

  return createServerClient<Database>( 
    SUPABASE_URL, 
    SUPABASE_ANON_KEY, 
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options) 
            );
          } catch {
          }
        },
      },
    }
  );
}