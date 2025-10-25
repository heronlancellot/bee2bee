import { useState, useEffect, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/integrations/supabase/hooks/useAuth';
import type { Tables } from '@/integrations/supabase/types';

export type UserProfile = Tables<'profiles'>;

export interface SelectedRepository {
  id: number;
  name: string;
  full_name: string;
  owner: string;
  description: string | null;
  language: string | null;
  stars: number;
}

export function useUserProfile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    if (!user?.id) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const { data, error: fetchError } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single();

      if (fetchError) {
        // If profile doesn't exist, create one
        if (fetchError.code === 'PGRST116') {
          const { data: newProfile, error: createError } = await supabase
            .from('profiles')
            .insert({
              id: user.id,
              full_name: user.user_metadata?.full_name || user.user_metadata?.name || null,
              avatar_url: user.user_metadata?.avatar_url || null,
              github_username: user.user_metadata?.user_name || user.user_metadata?.preferred_username || null,
            })
            .select()
            .single();

          if (createError) throw createError;
          setProfile(newProfile);
        } else {
          throw fetchError;
        }
      } else {
        setProfile(data);
      }
    } catch (err) {
      console.error('Error fetching profile:', err);
      setError(err instanceof Error ? err.message : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const updateProfile = useCallback(async (updates: Partial<Omit<UserProfile, 'id' | 'created_at'>>) => {
    if (!user?.id) {
      throw new Error('User not authenticated');
    }

    try {
      const { data, error: updateError } = await supabase
        .from('profiles')
        .update({
          ...updates,
          updated_at: new Date().toISOString(),
        })
        .eq('id', user.id)
        .select()
        .single();

      if (updateError) throw updateError;

      setProfile(data);
      return { success: true, data };
    } catch (err) {
      console.error('Error updating profile:', err);
      return {
        success: false,
        error: err instanceof Error ? err.message : 'Failed to update profile'
      };
    }
  }, [user]);

  const upsertProfile = useCallback(async (profileData: Partial<Omit<UserProfile, 'created_at' | 'updated_at'>>) => {
    if (!user?.id) {
      throw new Error('User not authenticated');
    }

    try {
      const { data, error: upsertError } = await supabase
        .from('profiles')
        .upsert({
          id: user.id,
          ...profileData,
          updated_at: new Date().toISOString(),
        })
        .select()
        .single();

      if (upsertError) throw upsertError;

      setProfile(data);
      return { success: true, data };
    } catch (err) {
      console.error('Error upserting profile:', err);
      return {
        success: false,
        error: err instanceof Error ? err.message : 'Failed to save profile'
      };
    }
  }, [user]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  return {
    profile,
    loading,
    error,
    updateProfile,
    upsertProfile,
    refetch: fetchProfile,
  };
}
