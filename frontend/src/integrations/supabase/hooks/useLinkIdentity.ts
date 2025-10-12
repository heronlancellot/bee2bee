import { useState } from 'react';
import { supabase } from '../client';

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
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to link GitHub account';
      setError(errorMessage);
      return { data: null, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const unlinkIdentity = async (identityId: string) => {
    try {
      setLoading(true);
      setError(null);

      const { data, error: unlinkError } = await supabase.auth.unlinkIdentity({
        identity_id: identityId,
      });

      if (unlinkError) throw unlinkError;

      return { data, error: null };
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to unlink identity';
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
