import { useState, useCallback } from 'react';
import { supabase } from '../client';
import type { AuthError } from '@supabase/supabase-js';

interface AuthResponse<T = unknown> {
  data: T | null;
  error: string | null;
}

export function useSignUp() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAuthError = useCallback((err: unknown): string => {
    if (err instanceof Error) {
      return err.message;
    }
    if (typeof err === 'object' && err !== null && 'message' in err) {
      return (err as AuthError).message;
    }
    return 'An unexpected error occurred';
  }, []);

  const executeAuth = useCallback(async <T,>(
    authFn: () => Promise<{ data: T; error: AuthError | null }>,
    fallbackError: string
  ): Promise<AuthResponse<T>> => {
    try {
      setLoading(true);
      setError(null);

      const result = await authFn();

      if (result.error) throw result.error;

      return { data: result.data, error: null };
    } catch (err) {
      const errorMessage = handleAuthError(err) || fallbackError;
      setError(errorMessage);
      return { data: null, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [handleAuthError]);

  const signUp = useCallback(
    async (email: string, password: string, fullName?: string) => {
      return executeAuth(
        async () => {
          const result = await supabase.auth.signUp({
            email,
            password,
            options: fullName ? { data: { full_name: fullName } } : undefined,
          });
          return result as any;
        },
        'Failed to sign up'
      );
    },
    [executeAuth]
  );

  const signInWithEmail = useCallback(
    async (email: string, password: string) => {
      return executeAuth(
        async () => {
          const result = await supabase.auth.signInWithPassword({ email, password });
          return result as any;
        },
        'Failed to sign in'
      );
    },
    [executeAuth]
  );

  const signInWithGithub = useCallback(async () => {
    return executeAuth(
      async () => {
        const result = await supabase.auth.signInWithOAuth({
          provider: 'github',
          options: {
            redirectTo: `${window.location.origin}/auth/callback`,
          },
        });
        return result as any;
      },
      'Failed to sign in with GitHub'
    );
  }, [executeAuth]);

  return {
    signUp,
    signInWithEmail,
    signInWithGithub,
    loading,
    error,
  };
}
