import { cn } from "@/lib/utils";

interface OnboardingProgressProps {
  currentStep: number;
  totalSteps: number;
}

export function OnboardingProgress({
  currentStep,
  totalSteps,
}: OnboardingProgressProps) {
  return (
    <div className="mb-8 flex flex-col items-center gap-2">
      <div className="flex items-center gap-2">
        {Array.from({ length: totalSteps }).map((_, index) => (
          <div
            key={index}
            className={cn(
              "h-2 w-2 rounded-full transition-all duration-300",
              index < currentStep
                ? "w-8 bg-primary"
                : index === currentStep
                  ? "bg-primary"
                  : "bg-muted-foreground/30",
            )}
          />
        ))}
      </div>
      <p className="text-xs text-muted-foreground">
        Step {currentStep + 1} of {totalSteps}
      </p>
    </div>
  );
}
