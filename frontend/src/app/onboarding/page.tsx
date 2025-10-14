"use client";

import { useState } from "react";
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
import { Label } from "@/components/ui/label";
import { HexagonBackground } from "@/components/ui/hexagon-background";
import { OnboardingProgress } from "@/components/onboarding-progress";

const motivations = [
  { id: "contribute", label: "I want to contribute to open source" },
  { id: "maintain", label: "I maintain projects and need help" },
  { id: "learn", label: "I want to learn from real codebases" },
  { id: "explore", label: "I'm exploring new technologies" },
];

const experienceLevels = [
  { id: "beginner", label: "Just starting", description: "0-1 years coding" },
  {
    id: "intermediate",
    label: "Getting comfortable",
    description: "1-3 years",
  },
  { id: "confident", label: "Confident", description: "3-5 years" },
  { id: "experienced", label: "Experienced", description: "5+ years" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [selectedMotivations, setSelectedMotivations] = useState<string[]>([]);
  const [experienceLevel, setExperienceLevel] = useState<string>("");

  const handleMotivationToggle = (id: string) => {
    setSelectedMotivations((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id],
    );
  };

  const handleContinue = () => {
    // TODO: Save preferences to backend
    console.log({ motivations: selectedMotivations, experienceLevel });
    router.push("/onboarding/interests");
  };

  const handleSkip = () => {
    router.push("/onboarding/interests");
  };

  return (
    <HexagonBackground
      hexagonSize={80}
      hexagonMargin={5}
      className="flex h-svh flex-col items-center justify-center p-4 md:p-6"
    >
      <div className="w-full max-w-2xl relative z-10 flex flex-col gap-4 max-h-full">
        <OnboardingProgress currentStep={0} totalSteps={4} />

        <Card className="flex-1 flex flex-col overflow-hidden">
          <CardHeader className="text-center shrink-0">
            <CardTitle className="text-xl md:text-2xl">Welcome, @username! 👋</CardTitle>
            <CardDescription className="text-sm">
              We&apos;re analyzing your GitHub profile right now. While we do that,
              tell us a bit about yourself.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 md:space-y-8 overflow-y-auto flex-1">
            <div className="space-y-4">
              <Label className="text-base font-medium">
                What brings you to Bee2Bee?
              </Label>
              <p className="text-sm text-muted-foreground">
                Select all that apply
              </p>
              <div className="space-y-3">
                {motivations.map((motivation) => (
                  <div
                    key={motivation.id}
                    className="flex items-center space-x-3"
                  >
                    <Checkbox
                      id={motivation.id}
                      checked={selectedMotivations.includes(motivation.id)}
                      onCheckedChange={() =>
                        handleMotivationToggle(motivation.id)
                      }
                      className="data-[state=checked]:border-primary data-[state=checked]:bg-primary"
                    />
                    <Label
                      htmlFor={motivation.id}
                      className="cursor-pointer text-sm font-normal"
                    >
                      {motivation.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <Label className="text-base font-medium">
                What&apos;s your experience level?
              </Label>
              <div className="grid grid-cols-2 gap-2">
                {experienceLevels.map((level) => (
                  <div
                    key={level.id}
                    onClick={() => setExperienceLevel(level.id)}
                    className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 p-3 transition-all ${
                      experienceLevel === level.id
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/50"
                    } `}
                  >
                    <div
                      className={`h-3 w-3 rounded-full border-2 transition-all mb-2 ${
                        experienceLevel === level.id
                          ? "border-primary bg-primary"
                          : "border-muted-foreground/50"
                      } `}
                    >
                      {experienceLevel === level.id && (
                        <div className="h-full w-full scale-50 rounded-full bg-white" />
                      )}
                    </div>
                    <p className="text-sm font-medium text-center">{level.label}</p>
                    <p className="text-xs text-muted-foreground text-center">
                      {level.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between pt-4">
              <Button
                variant="ghost"
                onClick={handleSkip}
                className="text-muted-foreground transition-colors hover:bg-transparent hover:text-primary"
              >
                Skip this step
              </Button>
              <Button
                onClick={handleContinue}
                className="bg-primary hover:bg-primary/90"
              >
                Continue →
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </HexagonBackground>
  );
}
