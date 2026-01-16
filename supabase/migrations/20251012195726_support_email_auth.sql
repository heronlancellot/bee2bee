-- Modify profiles table to support both email/password and GitHub OAuth auth

-- Make GitHub fields optional (they'll be NULL for email/password users)
ALTER TABLE public.profiles
  ALTER COLUMN github_username DROP NOT NULL,
  ALTER COLUMN github_id DROP NOT NULL;

-- Drop unique constraints on GitHub fields (users without GitHub can have NULL)
ALTER TABLE public.profiles
  DROP CONSTRAINT IF EXISTS profiles_github_username_key,
  DROP CONSTRAINT IF EXISTS profiles_github_id_key;

-- Add unique constraints that allow NULL (multiple NULLs are allowed)
CREATE UNIQUE INDEX profiles_github_username_key ON public.profiles(github_username) WHERE github_username IS NOT NULL;
CREATE UNIQUE INDEX profiles_github_id_key ON public.profiles(github_id) WHERE github_id IS NOT NULL;

-- Update the trigger function to handle both auth methods
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Check if it's a GitHub OAuth signup or email/password signup
  IF NEW.raw_app_meta_data->>'provider' = 'github' THEN
    -- GitHub OAuth signup - populate GitHub fields
    INSERT INTO public.profiles (id, github_username, github_id, avatar_url, full_name)
    VALUES (
      NEW.id,
      NEW.raw_user_meta_data->>'user_name',
      (NEW.raw_user_meta_data->>'provider_id')::BIGINT,
      NEW.raw_user_meta_data->>'avatar_url',
      NEW.raw_user_meta_data->>'full_name'
    );
  ELSE
    -- Email/password signup - create profile without GitHub data
    INSERT INTO public.profiles (id, full_name)
    VALUES (
      NEW.id,
      NEW.raw_user_meta_data->>'full_name'
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add a helper function to connect GitHub account later
CREATE OR REPLACE FUNCTION public.connect_github_account(
  user_id UUID,
  github_username_param TEXT,
  github_id_param BIGINT,
  avatar_url_param TEXT
)
RETURNS void AS $$
BEGIN
  UPDATE public.profiles
  SET
    github_username = github_username_param,
    github_id = github_id_param,
    avatar_url = avatar_url_param,
    updated_at = NOW()
  WHERE id = user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
