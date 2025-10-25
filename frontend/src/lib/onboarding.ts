/**
 * Onboarding utilities
 * Handles marking onboarding as complete for users
 */

import { supabase } from "@/integrations/supabase/client";

/**
 * Mark onboarding as completed for the current user
 * Updates user metadata in Supabase
 */
export async function completeOnboarding(): Promise<{ success: boolean; error?: string }> {
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser();

    if (userError || !user) {
      return { success: false, error: "User not authenticated" };
    }

    // Update user metadata to mark onboarding as complete
    const { error: updateError } = await supabase.auth.updateUser({
      data: {
        onboarding_completed: true,
        onboarding_completed_at: new Date().toISOString(),
      }
    });

    if (updateError) {
      console.error("Failed to mark onboarding as complete:", updateError);
      return { success: false, error: updateError.message };
    }

    console.log("Onboarding marked as complete");
    return { success: true };
  } catch (err) {
    console.error("Unexpected error completing onboarding:", err);
    return {
      success: false,
      error: err instanceof Error ? err.message : "Unknown error"
    };
  }
}

/**
 * Check if the current user has completed onboarding
 */
export async function hasCompletedOnboarding(): Promise<boolean> {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    return user?.user_metadata?.onboarding_completed === true;
  } catch {
    return false;
  }
}
