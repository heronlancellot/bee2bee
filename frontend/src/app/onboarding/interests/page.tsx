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
import { Label } from "@/components/ui/label";
import { HexagonBackground } from "@/components/ui/hexagon-background";
import { OnboardingProgress } from "@/components/onboarding-progress";
import { ChevronLeft } from "lucide-react";

const technologies = [
  "Python",
  "JavaScript",
  "TypeScript",
  "Go",
  "Rust",
  "Java",
  "C++",
  "Ruby",
  "PHP",
  "Swift",
  "Kotlin",
];

const domains = [
  "Web Development",
  "Mobile",
  "AI/ML",
  "DevOps",
  "Security",
  "Blockchain",
  "Game Dev",
  "Data Science",
];

const issueTypes = [
  { id: "bug-fixes", label: "Bug fixes" },
  { id: "new-features", label: "New features" },
  { id: "documentation", label: "Documentation" },
  { id: "testing", label: "Testing" },
  { id: "performance", label: "Performance optimization" },
];

export default function InterestsPage() {
  const router = useRouter();
  const [selectedTechnologies, setSelectedTechnologies] = useState<string[]>([]);
  const [selectedDomains, setSelectedDomains] = useState<string[]>([]);
  const [selectedIssueTypes, setSelectedIssueTypes] = useState<string[]>([]);

  const toggleTechnology = (tech: string) => {
    setSelectedTechnologies((prev) =>
      prev.includes(tech) ? prev.filter((t) => t !== tech) : [...prev, tech]
    );
  };

  const toggleDomain = (domain: string) => {
    setSelectedDomains((prev) =>
      prev.includes(domain) ? prev.filter((d) => d !== domain) : [...prev, domain]
    );
  };

  const toggleIssueType = (id: string) => {
    setSelectedIssueTypes((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleContinue = () => {
    // TODO: Save to backend
    console.log({
      technologies: selectedTechnologies,
      domains: selectedDomains,
      issueTypes: selectedIssueTypes,
    });
    router.push("/onboarding/analysis"); // Step 3
  };

  const handleSkip = () => {
    router.push("/onboarding/analysis"); // Step 3
  };

  const handleBack = () => {
    router.push("/onboarding");
  };

  return (
    <HexagonBackground
      hexagonSize={80}
      hexagonMargin={5}
      className="flex h-svh flex-col items-center justify-center p-4 md:p-6"
    >
      <div className="w-full max-w-2xl relative z-10 flex flex-col gap-4 max-h-full">
        <OnboardingProgress currentStep={1} totalSteps={4} />

        <Card className="flex-1 flex flex-col overflow-hidden">
          <CardHeader className="text-center shrink-0">
            <CardTitle className="text-xl md:text-2xl">What are you interested in?</CardTitle>
            <CardDescription className="text-sm">
              This helps us find better matches for you.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 md:space-y-6 overflow-y-auto flex-1">
            {/* Technologies */}
            <div className="space-y-3">
              <Label className="text-base font-medium">
                Technologies
              </Label>
              <p className="text-xs text-muted-foreground">
                Select your favorites
              </p>
              <div className="flex flex-wrap gap-2">
                {technologies.map((tech) => (
                  <button
                    key={tech}
                    type="button"
                    onClick={() => toggleTechnology(tech)}
                    className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-300 ${
                      selectedTechnologies.includes(tech)
                        ? "bg-primary/10 backdrop-blur-sm text-primary border border-primary/30 shadow-[0_0_8px_hsl(var(--secondary-accent)/0.2)]"
                        : "bg-muted/30 backdrop-blur-sm border border-border/30 text-muted-foreground hover:bg-muted/50 hover:border-primary/20 hover:text-primary hover:shadow-[0_0_4px_hsl(var(--primary)/0.15)]"
                    }`}
                    style={{
                      boxShadow: selectedTechnologies.includes(tech) ? undefined : '0 1px 2px rgba(0, 0, 0, 0.05)'
                    }}
                  >
                    {tech}
                  </button>
                ))}
              </div>
            </div>

            {/* Domains */}
            <div className="space-y-3">
              <Label className="text-base font-medium">
                Domains
              </Label>
              <div className="flex flex-wrap gap-2">
                {domains.map((domain) => (
                  <button
                    key={domain}
                    type="button"
                    onClick={() => toggleDomain(domain)}
                    className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-300 ${
                      selectedDomains.includes(domain)
                        ? "bg-primary/10 backdrop-blur-sm text-primary border border-primary/30 shadow-[0_0_8px_hsl(var(--secondary-accent)/0.2)]"
                        : "bg-muted/30 backdrop-blur-sm border border-border/30 text-muted-foreground hover:bg-muted/50 hover:border-primary/20 hover:text-primary hover:shadow-[0_0_4px_hsl(var(--primary)/0.15)]"
                    }`}
                    style={{
                      boxShadow: selectedDomains.includes(domain) ? undefined : '0 1px 2px rgba(0, 0, 0, 0.05)'
                    }}
                  >
                    {domain}
                  </button>
                ))}
              </div>
            </div>

            {/* Issue Types */}
            <div className="space-y-3">
              <Label className="text-base font-medium">
                Issue types you prefer
              </Label>
              <div className="flex flex-wrap gap-2">
                {issueTypes.map((issueType) => (
                  <button
                    key={issueType.id}
                    type="button"
                    onClick={() => toggleIssueType(issueType.id)}
                    className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-300 ${
                      selectedIssueTypes.includes(issueType.id)
                        ? "bg-primary/10 backdrop-blur-sm text-primary border border-primary/30 shadow-[0_0_8px_hsl(var(--secondary-accent)/0.2)]"
                        : "bg-muted/30 backdrop-blur-sm border border-border/30 text-muted-foreground hover:bg-muted/50 hover:border-primary/20 hover:text-primary hover:shadow-[0_0_4px_hsl(var(--primary)/0.15)]"
                    }`}
                    style={{
                      boxShadow: selectedIssueTypes.includes(issueType.id) ? undefined : '0 1px 2px rgba(0, 0, 0, 0.05)'
                    }}
                  >
                    {issueType.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4">
              <Button
                variant="ghost"
                onClick={handleBack}
                className="text-muted-foreground transition-colors hover:bg-transparent hover:text-primary"
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
              <div className="flex gap-2">
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
            </div>
          </CardContent>
        </Card>
      </div>
    </HexagonBackground>
  );
}
