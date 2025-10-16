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
import { HexagonBackground } from "@/components/ui/hexagon-background";
import { OnboardingProgress } from "@/components/onboarding-progress";
import { Check, Loader2, ChevronLeft, Star, BookMarked, Code } from "lucide-react";
import Image from "next/image";
import * as SiIcons from "react-icons/si";

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

// Generate mock heatmap data (52 weeks)
const generateHeatmapData = () => {
  const weeks = 52;
  const data = [];
  for (let i = 0; i < weeks; i++) {
    data.push(Math.floor(Math.random() * 5)); // 0-4 contribution levels
  }
  return data;
};

const mockResults = {
  profile: {
    avatar: "https://github.com/github.png",
    name: "Lucas Oshan",
    username: "lucasoshan",
    followers: 342,
    following: 187,
  },
  stats: {
    totalStars: 342,
    totalForks: 87,
    publicRepos: 24,
    contributions: 1247,
  },
  languages: [
    { name: "Python", percentage: 60 },
    { name: "JavaScript", percentage: 30 },
    { name: "Go", percentage: 10 },
  ],
  heatmap: generateHeatmapData(),
  repositories: [
    {
      id: 1,
      name: "awesome-project",
      owner: "lucasoshan",
      full_name: "lucasoshan/awesome-project",
      description: "A really cool project that does amazing things with React and TypeScript",
      stars: 124,
      language: "TypeScript",
    },
    {
      id: 2,
      name: "python-ml-toolkit",
      owner: "lucasoshan",
      full_name: "lucasoshan/python-ml-toolkit",
      description: "Machine learning toolkit for data scientists",
      stars: 89,
      language: "Python",
    },
    {
      id: 3,
      name: "go-microservices",
      owner: "lucasoshan",
      full_name: "lucasoshan/go-microservices",
      description: "Scalable microservices architecture built with Go",
      stars: 56,
      language: "Go",
    },
  ],
};

export default function AnalysisPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  // Loading animation
  useEffect(() => {
    if (currentStep < loadingSteps.length) {
      const timer = setTimeout(() => {
        setCurrentStep((prev) => prev + 1);
      }, loadingSteps[currentStep]?.duration || 1500);

      return () => clearTimeout(timer);
    } else {
      setIsComplete(true);
    }
  }, [currentStep]);

  const handleContinue = () => {
    router.push("/onboarding/repositories"); // Step 4 - Repository selection
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
        <OnboardingProgress currentStep={2} totalSteps={4} />

        <Card className="flex-1 flex flex-col overflow-hidden dark:bg-[hsl(var(--surface-elevated))]">
          <CardHeader className="text-center shrink-0">
            <CardTitle className="text-xl md:text-2xl">
              {isComplete ? "Analysis Complete!" : "Analyzing your GitHub..."}
            </CardTitle>
            <CardDescription className="text-sm">
              {isComplete
                ? mockResults.repositories.length > 0
                  ? `Found ${mockResults.repositories.length} ${mockResults.repositories.length === 1 ? 'repository' : 'repositories'} in your account`
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
                    src={mockResults.profile.avatar}
                    alt={mockResults.profile.name}
                    width={48}
                    height={48}
                    className="rounded-lg border-2 border-border/50"
                  />
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold truncate">
                      {mockResults.profile.name}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>@{mockResults.profile.username}</span>
                      <span>·</span>
                      <span>{mockResults.stats.publicRepos} repos</span>
                      <span>·</span>
                      <div className="flex items-center gap-1">
                        <Star className="h-2.5 w-2.5 text-yellow-500" />
                        <span>{mockResults.stats.totalStars}</span>
                      </div>
                    </div>
                  </div>
                  {/* Compact Languages */}
                  <div className="flex gap-1">
                    {mockResults.languages.map((lang) => {
                      const Icon = languageIcons[lang.name];
                      return Icon ? <Icon key={lang.name} className="h-4 w-4" /> : null;
                    })}
                  </div>
                </div>

                {/* Repository Cards */}
                {mockResults.repositories.length > 0 ? (
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-muted-foreground px-1">
                      Your repositories ({mockResults.repositories.length})
                    </h4>
                    {mockResults.repositories.map((repo) => {
                      return (
                        <div
                          key={repo.id}
                          className="group relative flex items-start gap-2.5 p-2.5 rounded-lg border border-border/40 bg-muted/20 hover:bg-muted/30 hover:border-primary/50 transition-all duration-200 cursor-pointer"
                        >
                          <BookMarked className="h-3.5 w-3.5 shrink-0 text-muted-foreground group-hover:text-primary transition-colors mt-0.5" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold truncate group-hover:text-primary transition-colors mb-0.5">
                              {repo.owner}/{repo.name}
                            </p>
                            <p className="text-xs text-muted-foreground line-clamp-1">
                              {repo.description}
                            </p>
                          </div>
                          <div className="flex items-center gap-0.5 text-xs text-muted-foreground shrink-0">
                            <Star className="h-3 w-3 text-yellow-500" />
                            <span>{repo.stars}</span>
                          </div>
                        </div>
                      );
                    })}
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
                  className="text-muted-foreground transition-colors hover:bg-transparent hover:text-primary"
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Back
                </Button>
                <Button
                  onClick={handleContinue}
                  className="bg-primary hover:bg-primary/90"
                >
                  {mockResults.repositories.length > 0
                    ? "Select repositories →"
                    : "Add repositories →"}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </HexagonBackground>
  );
}
