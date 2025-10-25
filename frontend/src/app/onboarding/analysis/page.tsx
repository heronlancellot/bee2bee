"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { HexagonBackground } from "@/components/ui/hexagon-background";
import { OnboardingProgress } from "@/components/onboarding-progress";
import { Check, Loader2, ChevronLeft, Star, BookMarked, Code } from "lucide-react";
import Image from "next/image";
import * as SiIcons from "react-icons/si";
import { useAuth } from "@/integrations/supabase/hooks/useAuth";
import { useGitHubRepositories } from "@/hooks/useGitHubRepositories";
import { completeOnboarding } from "@/lib/onboarding";
import { supabase } from "@/integrations/supabase/client";

const languageIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  Python: SiIcons.SiPython,
  JavaScript: SiIcons.SiJavascript,
  TypeScript: SiIcons.SiTypescript,
  Go: SiIcons.SiGo,
  Rust: SiIcons.SiRust,
  Java: Code, // SiJava doesn't exist in react-icons
  "C++": SiIcons.SiCplusplus,
  Ruby: SiIcons.SiRuby,
  PHP: SiIcons.SiPhp,
  Swift: SiIcons.SiSwift,
  Kotlin: SiIcons.SiKotlin,
};

const loadingSteps = [
  { id: "profile", label: "Loading GitHub profile...", duration: 1500 },
  { id: "repos", label: "Fetching your repositories...", duration: 2000 },
  { id: "analyzing", label: "Analyzing your code and contributions...", duration: 2500 },
  { id: "matching", label: "Finding repositories that match your interests...", duration: 2000 },
];

export default function AnalysisPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { repositories, user: githubUser, loading: githubLoading } = useGitHubRepositories();
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [selectedRepos, setSelectedRepos] = useState<number[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  // Calculate real stats from repositories
  const totalStars = repositories.reduce((sum, repo) => sum + repo.stargazers_count, 0);
  const publicRepos = repositories.length;

  // Get top languages from repositories
  const languageCounts = repositories.reduce((acc, repo) => {
    if (repo.language) {
      acc[repo.language] = (acc[repo.language] || 0) + 1;
    }
    return acc;
  }, {} as Record<string, number>);

  const topLanguages = Object.entries(languageCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3)
    .map(([name, count]) => ({
      name,
      percentage: Math.round((count / repositories.length) * 100)
    }));

  // Use real user data or fallback to metadata
  const profile = {
    avatar: githubUser?.avatar_url || user?.user_metadata?.avatar_url || "https://github.com/github.png",
    name: githubUser?.name || user?.user_metadata?.full_name || "User",
    username: githubUser?.login || user?.user_metadata?.user_name || user?.user_metadata?.preferred_username || "user",
    followers: githubUser?.followers || 0,
    following: githubUser?.following || 0,
  };

  // Loading animation - auto-complete when GitHub data is loaded
  useEffect(() => {
    if (currentStep < loadingSteps.length && !githubLoading) {
      const timer = setTimeout(() => {
        setCurrentStep((prev) => prev + 1);
      }, loadingSteps[currentStep]?.duration || 1500);

      return () => clearTimeout(timer);
    } else if (currentStep >= loadingSteps.length) {
      setIsComplete(true);
    }
  }, [currentStep, githubLoading]);

  const handleToggleRepo = (repoId: number) => {
    setSelectedRepos((prev) =>
      prev.includes(repoId)
        ? prev.filter((id) => id !== repoId)
        : [...prev, repoId]
    );
  };

  const handleContinue = async () => {
    setIsSaving(true);
    try {
      // Save selected repositories to user metadata
      const selectedRepoData = repositories
        .filter((repo) => selectedRepos.includes(repo.id))
        .map((repo) => ({
          id: repo.id,
          name: repo.name,
          full_name: repo.full_name,
          owner: repo.owner.login,
          description: repo.description,
          language: repo.language,
          stars: repo.stargazers_count,
        }));

      // Update user metadata with selected repositories
      const { data: { user: authUser } } = await supabase.auth.getUser();
      if (authUser) {
        await supabase.auth.updateUser({
          data: {
            selected_repositories: selectedRepoData,
          },
        });
      }

      // Mark onboarding as complete
      await completeOnboarding();

      // Redirect to dashboard
      router.push("/dashboard");
    } catch (error) {
      console.error("Error saving repositories:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleBack = () => {
    router.push("/onboarding/interests");
  };

  return (
    <HexagonBackground
      hexagonSize={80}
      hexagonMargin={5}
      className="flex h-svh flex-col items-center justify-center p-4 md:p-6"
    >
      <div className="w-full max-w-2xl relative z-10 flex flex-col gap-4 max-h-full">
        <OnboardingProgress currentStep={2} totalSteps={3} />

        <Card className="flex-1 flex flex-col overflow-hidden dark:bg-[hsl(var(--surface-elevated))]">
          <CardHeader className="text-center shrink-0">
            <CardTitle className="text-xl md:text-2xl">
              {isComplete ? "Select Your Repositories" : "Analyzing your GitHub..."}
            </CardTitle>
            <CardDescription className="text-sm">
              {isComplete
                ? repositories.length > 0
                  ? "Choose the repositories you want to track and collaborate on"
                  : "No public repositories found in your account"
                : "This usually takes a few seconds..."}
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4 overflow-y-auto flex-1">
            {/* Loading Section */}
            {!isComplete && (
              <div className="space-y-3 p-4 border border-border/50 rounded-lg bg-muted/20">
                {loadingSteps.map((step, index) => (
                  <div key={step.id} className="flex items-center gap-3">
                    {index < currentStep ? (
                      <Check className="h-4 w-4 text-primary shrink-0" />
                    ) : index === currentStep ? (
                      <Loader2 className="h-4 w-4 text-primary animate-spin shrink-0" />
                    ) : (
                      <div className="h-4 w-4 rounded-full border-2 border-muted-foreground/30 shrink-0" />
                    )}
                    <span
                      className={`text-sm ${
                        index <= currentStep
                          ? "text-foreground"
                          : "text-muted-foreground"
                      }`}
                    >
                      {step.label}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Results Section - Shows repos after loading */}
            {isComplete && (
              <div className="space-y-4">
                {/* Profile Summary - Compact */}
                <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/20 border border-border/30">
                  <Image
                    src={profile.avatar}
                    alt={profile.name}
                    width={48}
                    height={48}
                    className="rounded-lg border-2 border-border/50"
                  />
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold truncate">
                      {profile.name}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>@{profile.username}</span>
                      <span>·</span>
                      <span>{publicRepos} repos</span>
                      <span>·</span>
                      <div className="flex items-center gap-1">
                        <Star className="h-2.5 w-2.5 text-yellow-500" />
                        <span>{totalStars}</span>
                      </div>
                    </div>
                  </div>
                  {/* Compact Languages */}
                  <div className="flex gap-1">
                    {topLanguages.map((lang) => {
                      const Icon = languageIcons[lang.name];
                      return Icon ? <Icon key={lang.name} className="h-4 w-4" /> : null;
                    })}
                  </div>
                </div>

                {/* Repository Cards */}
                {repositories.length > 0 ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between px-1">
                      <h4 className="text-sm font-medium text-muted-foreground">
                        Select repositories to track ({selectedRepos.length} selected)
                      </h4>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          if (selectedRepos.length === repositories.length) {
                            setSelectedRepos([]);
                          } else {
                            setSelectedRepos(repositories.map((r) => r.id));
                          }
                        }}
                        className="h-6 text-xs text-muted-foreground hover:text-primary"
                      >
                        {selectedRepos.length === repositories.length
                          ? "Deselect all"
                          : "Select all"}
                      </Button>
                    </div>
                    <div className="space-y-1.5 max-h-[400px] overflow-y-auto pr-1">
                      {repositories.map((repo) => {
                        const isSelected = selectedRepos.includes(repo.id);
                        return (
                          <div
                            key={repo.id}
                            onClick={() => handleToggleRepo(repo.id)}
                            className={`group relative flex items-start gap-2.5 p-2.5 rounded-lg border transition-all duration-200 cursor-pointer ${
                              isSelected
                                ? "border-primary bg-primary/5"
                                : "border-border/40 bg-muted/20 hover:bg-muted/30 hover:border-primary/50"
                            }`}
                          >
                            <Checkbox
                              checked={isSelected}
                              onCheckedChange={() => handleToggleRepo(repo.id)}
                              className="mt-0.5 shrink-0"
                            />
                            <BookMarked
                              className={`h-3.5 w-3.5 shrink-0 transition-colors mt-0.5 ${
                                isSelected
                                  ? "text-primary"
                                  : "text-muted-foreground group-hover:text-primary"
                              }`}
                            />
                            <div className="flex-1 min-w-0">
                              <p
                                className={`text-sm font-semibold truncate transition-colors mb-0.5 ${
                                  isSelected
                                    ? "text-primary"
                                    : "group-hover:text-primary"
                                }`}
                              >
                                {repo.owner.login}/{repo.name}
                              </p>
                              <p className="text-xs text-muted-foreground line-clamp-1">
                                {repo.description || "No description available"}
                              </p>
                            </div>
                            <div className="flex items-center gap-0.5 text-xs text-muted-foreground shrink-0">
                              <Star className="h-3 w-3 text-yellow-500" />
                              <span>{repo.stargazers_count}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="text-center p-8 rounded-lg bg-muted/20 border border-border/30">
                    <p className="text-sm text-muted-foreground mb-2">
                      No repositories found
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Looks like you don&apos;t have any public repositories yet
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Actions */}
            {isComplete && (
              <div className="flex items-center justify-between pt-4">
                <Button
                  variant="ghost"
                  onClick={handleBack}
                  disabled={isSaving}
                  className="text-muted-foreground transition-colors hover:bg-transparent hover:text-primary"
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Back
                </Button>
                <Button
                  onClick={handleContinue}
                  disabled={isSaving}
                  className="bg-primary hover:bg-primary/90"
                >
                  {isSaving ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      {selectedRepos.length > 0
                        ? `Continue with ${selectedRepos.length} ${selectedRepos.length === 1 ? 'repo' : 'repos'} →`
                        : "Skip for now →"}
                    </>
                  )}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </HexagonBackground>
  );
}
