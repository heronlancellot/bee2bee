import { useState } from 'react';
import { supabase } from '../client';
import type { UserIdentity } from '@supabase/supabase-js';

export function useLinkIdentity() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const linkGitHub = async () => {
    try {
      setLoading(true);
      setError(null);

      // Link GitHub to current logged-in account
      const { data, error: linkError } = await supabase.auth.linkIdentity({
        provider: 'github',
      });

      if (linkError) throw linkError;

      return { data, error: null };
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to link GitHub account';
      setError(errorMessage);
      return { data: null, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const unlinkIdentity = async (identity: UserIdentity) => {
    try {
      setLoading(true);
      setError(null);

      const { data, error: unlinkError } = await supabase.auth.unlinkIdentity(identity);

      if (unlinkError) throw unlinkError;

      return { data, error: null };
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to unlink identity';
      setError(errorMessage);
      return { data: null, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  return {
    linkGitHub,
    unlinkIdentity,
    loading,
    error,
  };
}
