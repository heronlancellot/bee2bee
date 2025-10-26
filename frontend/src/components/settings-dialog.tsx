"use client";

import * as React from "react";
import {
  Github,
  Settings2,
  CreditCard,
  BarChart3,
  Check,
  Download,
  Search,
  ArrowUpDown,
  GitBranch,
  Star,
  X,
  BookMarked,
  Loader2,
} from "lucide-react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { useAuth } from "@/integrations/supabase/hooks/useAuth";
import { useLinkIdentity } from "@/integrations/supabase/hooks/useLinkIdentity";
import { useRepositoryStore } from "@/store/repositories";
import { toast } from "sonner";
import { useGitHubRepositories } from "@/hooks/useGitHubRepositories";

type SettingsSection = "github" | "preferences" | "plans" | "usage";

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface SidebarSection {
  label: string;
  items: {
    id: SettingsSection;
    label: string;
    icon: any;
  }[];
}

export function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
  const [activeSection, setActiveSection] =
    React.useState<SettingsSection>("github");

  const sections: SidebarSection[] = [
    {
      label: "Workspace",
      items: [
        {
          id: "preferences" as SettingsSection,
          label: "Preferences",
          icon: Settings2,
        },
      ],
    },
    {
      label: "Account",
      items: [
        {
          id: "plans" as SettingsSection,
          label: "Plans & Billing",
          icon: CreditCard,
        },
        {
          id: "usage" as SettingsSection,
          label: "Usage",
          icon: BarChart3,
        },
      ],
    },
    {
      label: "Integrations",
      items: [
        {
          id: "github" as SettingsSection,
          label: "GitHub",
          icon: Github,
        },
      ],
    },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="h-[85vh] max-h-[700px] max-w-5xl gap-0 bg-background p-0 dark:bg-[hsl(var(--surface-elevated))]">
        <div className="flex h-full overflow-hidden">
          {/* Sidebar */}
          <div className="flex w-64 flex-col gap-5 overflow-y-auto border-r bg-muted/30 p-4 dark:border-white/5 dark:bg-[hsl(var(--surface-elevated))]">
            {sections.map((section, sectionIndex) => (
              <div key={sectionIndex} className="space-y-1">
                {/* Section Label */}
                <div className="px-3 py-1.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/60">
                    {section.label}
                  </span>
                </div>

                {/* Section Items */}
                <div className="space-y-0.5">
                  {section.items.map((item) => {
                    const Icon = item.icon;
                    return (
                      <button
                        key={item.id}
                        onClick={() => setActiveSection(item.id)}
                        className={cn(
                          "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all duration-200",
                          activeSection === item.id
                            ? "border border-border/50 bg-secondary font-semibold text-foreground shadow-sm dark:border-border dark:bg-muted"
                            : "text-muted-foreground hover:bg-muted/40 hover:text-foreground dark:hover:bg-muted/60",
                        )}
                      >
                        <Icon className="h-4 w-4 shrink-0" />
                        <span className="font-medium">{item.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-8">
              {activeSection === "github" && <IntegrationsContent />}
              {activeSection === "preferences" && <PreferencesContent />}
              {activeSection === "plans" && <PlansContent />}
              {activeSection === "usage" && <UsageContent />}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function IntegrationsContent() {
  const { user } = useAuth();
  const {
    linkGitHub,
    unlinkIdentity,
    loading: linkLoading,
  } = useLinkIdentity();

  // Get GitHub repos
  const { repositories: githubRepos, loading: githubLoading } = useGitHubRepositories();

  // Store state
  const storeRepositories = useRepositoryStore((state) => state.repositories);

  const [searchRepo, setSearchRepo] = React.useState("");
  const [showRepoSelector, setShowRepoSelector] = React.useState(false);
  const [localSelectedRepos, setLocalSelectedRepos] = React.useState<number[]>([]);

  // Repository handlers
  const handleRemoveRepo = React.useCallback((repoId: string) => {
    useRepositoryStore.getState().removeRepository(repoId);
  }, []);

  const handleToggleFavorite = React.useCallback((repoId: string) => {
    useRepositoryStore.getState().toggleFavorite(repoId);
  }, []);

  const handleToggleGitHubRepo = (repoId: number) => {
    setLocalSelectedRepos((prev) =>
      prev.includes(repoId)
        ? prev.filter((id) => id !== repoId)
        : [...prev, repoId]
    );
  };

  const handleAddRepositories = () => {
    const selectedRepoData = githubRepos.filter((r) =>
      localSelectedRepos.includes(r.id)
    );
    selectedRepoData.forEach((repo) => {
      useRepositoryStore.getState().addRepository({
        id: repo.id.toString(),
        name: repo.name,
        full_name: repo.full_name,
        owner: repo.owner.login,
        description: repo.description,
        is_private: repo.private,
        is_favorite: false,
        language: repo.language,
        stars: repo.stargazers_count,
        indexed_at: null,
        complexity_score: null,
        agent_id: null,
      });
    });
    setLocalSelectedRepos([]);
    setShowRepoSelector(false);
    toast.success(`Added ${selectedRepoData.length} repositories!`);
  };

  // DEV BYPASS: Force GitHub to be connected in development
  // Use a stable mock object to prevent infinite re-renders
  const devBypassIdentity = React.useRef({
    id: "dev-bypass-id",
    user_id: "dev-bypass-user",
    identity_id: "dev-bypass-identity-id",
    provider: "github",
    identity_data: {},
    last_sign_in_at: new Date().toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  });

  const githubIdentity = React.useMemo(() => {
    if (process.env.NEXT_PUBLIC_DEV_BYPASS_AUTH === "true") {
      return devBypassIdentity.current;
    }
    return user?.identities?.find((identity) => identity.provider === "github");
  }, [user?.identities]);

  const githubConnected = !!githubIdentity;

  const handleConnectGitHub = React.useCallback(async () => {
    const { error } = await linkGitHub();
    if (error) {
      toast.error("Failed to connect GitHub", { description: error });
    } else {
      toast.success("GitHub connected successfully!");
    }
  }, [linkGitHub]);

  const handleDisconnectGitHub = React.useCallback(async () => {
    if (!githubIdentity) return;

    // DEV BYPASS: Skip actual disconnection in development
    if (process.env.NEXT_PUBLIC_DEV_BYPASS_AUTH === "true") {
      toast.info("Dev Mode", {
        description: "GitHub disconnect bypassed in development mode",
      });
      return;
    }

    const { error } = await unlinkIdentity(githubIdentity);
    if (error) {
      toast.error("Failed to disconnect GitHub", { description: error });
    } else {
      toast.success("GitHub disconnected successfully!");
    }
  }, [githubIdentity, unlinkIdentity]);

  const filteredRepos = React.useMemo(
    () =>
      storeRepositories.filter(
        (r) =>
          r.name.toLowerCase().includes(searchRepo.toLowerCase()) ||
          r.owner.toLowerCase().includes(searchRepo.toLowerCase()),
      ),
    [storeRepositories, searchRepo],
  );

  return (
    <div className="max-w-3xl space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">GitHub</h2>
        <p className="text-muted-foreground">
          Connect your GitHub account to sync and analyze your repositories
        </p>
      </div>

      <Separator className="dark:bg-white/5" />

      {/* Connection Card */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Connection
        </h3>
        <div className="flex items-center justify-between rounded-xl border bg-card p-6 shadow-sm backdrop-blur-sm transition-shadow duration-200 hover:shadow-md dark:border-white/10 dark:bg-[hsl(var(--surface-elevated))]/50">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl border bg-[#24292e] shadow-md dark:border-border dark:bg-foreground">
              <Github className="h-6 w-6 text-primary-foreground dark:text-background" />
            </div>
            <div className="space-y-1">
              <h4 className="font-semibold">GitHub Account</h4>
              <p className="text-sm text-muted-foreground">
                {githubConnected ? "Connected and syncing" : "Not connected"}
              </p>
            </div>
          </div>
          {githubConnected ? (
            <Button
              variant="outline"
              onClick={handleDisconnectGitHub}
              disabled={linkLoading}
              className="border-border hover:bg-[hsl(var(--secondary-accent))] hover:text-white dark:border-white/20 dark:hover:bg-[hsl(var(--primary))] dark:hover:text-white"
            >
              {linkLoading ? "Disconnecting..." : "Disconnect"}
            </Button>
          ) : (
            <Button
              onClick={handleConnectGitHub}
              disabled={linkLoading}
              className="bg-[hsl(var(--secondary-accent))] hover:bg-[hsl(var(--secondary-accent))]/80 dark:bg-[hsl(var(--primary))] dark:hover:bg-[hsl(var(--primary))]/90"
            >
              {linkLoading ? "Connecting..." : "Connect GitHub"}
            </Button>
          )}
        </div>
      </div>

      {/* Repository Management */}
      {githubConnected && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Manage Repositories
            </h3>
            <Button
              size="sm"
              onClick={() => setShowRepoSelector(!showRepoSelector)}
              className="bg-[hsl(var(--secondary-accent))] hover:bg-[hsl(var(--secondary-accent))]/80 dark:bg-[hsl(var(--primary))] dark:hover:bg-[hsl(var(--primary))]/90"
            >
              {showRepoSelector ? "Close" : "Add More Repositories"}
            </Button>
          </div>

          {/* GitHub Repository Selector */}
          {showRepoSelector && (
            <div className="space-y-3 rounded-xl border bg-card p-4 shadow-sm backdrop-blur-sm dark:border-white/10 dark:bg-[hsl(var(--surface-elevated))]/50">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold">
                  Select repositories from your GitHub ({localSelectedRepos.length} selected)
                </h4>
              </div>
              {githubLoading ? (
                <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Loading repositories...
                </div>
              ) : githubRepos.length === 0 ? (
                <div className="py-8 text-center text-sm text-muted-foreground">
                  No repositories found
                </div>
              ) : (
                <>
                  <div className="max-h-[400px] space-y-2 overflow-y-auto pr-2">
                    {githubRepos.map((repo) => {
                      const isSelected = localSelectedRepos.includes(repo.id);
                      return (
                        <div
                          key={repo.id}
                          onClick={() => handleToggleGitHubRepo(repo.id)}
                          className={`group relative flex cursor-pointer items-start gap-2.5 rounded-lg border p-2.5 transition-all duration-200 ${
                            isSelected
                              ? "border-primary bg-primary/5"
                              : "border-border/40 bg-muted/20 hover:border-primary/50 hover:bg-muted/30"
                          }`}
                        >
                          <Checkbox
                            checked={isSelected}
                            className="pointer-events-none mt-0.5 shrink-0"
                          />
                          <BookMarked
                            className={`mt-0.5 h-3.5 w-3.5 shrink-0 transition-colors ${
                              isSelected
                                ? "text-primary"
                                : "text-muted-foreground group-hover:text-primary"
                            }`}
                          />
                          <div className="min-w-0 flex-1">
                            <p
                              className={`mb-0.5 truncate text-sm font-semibold transition-colors ${
                                isSelected
                                  ? "text-primary"
                                  : "group-hover:text-primary"
                              }`}
                            >
                              {repo.owner.login}/{repo.name}
                            </p>
                            <p className="line-clamp-1 text-xs text-muted-foreground">
                              {repo.description || "No description available"}
                            </p>
                          </div>
                          <div className="flex shrink-0 items-center gap-0.5 text-xs text-muted-foreground">
                            <Star className="h-3 w-3 text-yellow-500" />
                            <span>{repo.stargazers_count}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  {localSelectedRepos.length > 0 && (
                    <Button
                      onClick={handleAddRepositories}
                      className="w-full bg-primary hover:bg-primary/90"
                    >
                      Add {localSelectedRepos.length}{" "}
                      {localSelectedRepos.length === 1
                        ? "repository"
                        : "repositories"}
                    </Button>
                  )}
                </>
              )}
            </div>
          )}
          {/* Search */}
          <div className="relative">
            <Search className="pointer-events-none absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground/50" />
            <Input
              type="text"
              placeholder="Search repositories..."
              value={searchRepo}
              onChange={(e) => setSearchRepo(e.target.value)}
              className="border-border/50 bg-muted/40 pl-8 pr-8 focus:border-primary/30 focus:bg-background"
            />
            {searchRepo && (
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-1 top-1 h-7 w-7 p-0"
                onClick={() => setSearchRepo("")}
              >
                <X className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>

          {/* Repository List */}
          <div className="overflow-hidden rounded-xl border bg-card shadow-sm backdrop-blur-sm dark:border-white/10 dark:bg-[hsl(var(--surface-elevated))]/50">
            {filteredRepos.length === 0 ? (
              <div className="p-8 text-center">
                <p className="text-sm text-muted-foreground">
                  {searchRepo
                    ? "No repositories found"
                    : "No repositories selected"}
                </p>
              </div>
            ) : (
              <div className="divide-y dark:divide-white/5">
                {filteredRepos.map((repo) => (
                  <div
                    key={repo.id}
                    className="flex items-center justify-between p-4 transition-colors hover:bg-muted/50 dark:hover:bg-white/5"
                  >
                    <div className="flex min-w-0 flex-1 items-center gap-3">
                      <GitBranch className="h-4 w-4 shrink-0 text-muted-foreground/60" />
                      <div className="flex min-w-0 items-center gap-2">
                        <p className="truncate text-sm text-muted-foreground">
                          {repo.owner}/
                        </p>
                        <p className="truncate text-sm font-semibold">
                          {repo.name}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleToggleFavorite(repo.id)}
                        className="rounded-md p-1.5 transition-colors hover:bg-muted"
                        aria-label={
                          repo.is_favorite
                            ? "Remove from favorites"
                            : "Add to favorites"
                        }
                      >
                        <Star
                          className={cn(
                            "h-4 w-4 transition-all",
                            repo.is_favorite
                              ? "fill-primary text-primary"
                              : "text-muted-foreground/40 hover:text-primary",
                          )}
                        />
                      </button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveRepo(repo.id)}
                        className="h-8 px-3 text-xs text-destructive hover:bg-destructive/10 hover:text-destructive"
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <p className="text-xs text-muted-foreground">
            You have {storeRepositories.length}{" "}
            {storeRepositories.length === 1 ? "repository" : "repositories"} selected
          </p>
        </div>
      )}
    </div>
  );
}

function PreferencesContent() {
  const [notifications, setNotifications] = React.useState(true);

  return (
    <div className="relative max-w-3xl space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Preferences</h2>
        <p className="text-muted-foreground">
          Customize your experience and notification settings
        </p>
      </div>

      <Separator className="dark:bg-white/5" />

      {/* Blurred Content */}
      <div className="relative">
        {/* Notifications Section - Blurred */}
        <div className="pointer-events-none select-none space-y-4 opacity-50 blur-sm">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Notifications
          </h3>
          <div className="flex items-center justify-between rounded-xl border bg-card p-6 shadow-sm backdrop-blur-sm transition-shadow duration-200 hover:shadow-md dark:border-white/10 dark:bg-[hsl(var(--surface-elevated))]/50">
            <div className="space-y-1">
              <Label
                htmlFor="notifications"
                className="cursor-pointer text-base font-semibold"
              >
                Email Notifications
              </Label>
              <p className="text-sm text-muted-foreground">
                Receive notifications about your repositories
              </p>
            </div>
            <Switch
              id="notifications"
              checked={notifications}
              onCheckedChange={setNotifications}
            />
          </div>
        </div>

        {/* Coming Soon Overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="space-y-2 text-center">
            <h3 className="text-3xl font-bold text-foreground">Coming Soon</h3>
            <p className="text-sm text-muted-foreground">
              Preferences will be available soon
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function PlansContent() {
  const [currentPlan, setCurrentPlan] = React.useState("free");
  const [searchInvoice, setSearchInvoice] = React.useState("");
  const [sortOrder, setSortOrder] = React.useState<"asc" | "desc">("desc");

  const plans = [
    {
      id: "free",
      name: "Free plan",
      price: "$0",
      period: "/mth",
      features: ["Up to 3 repositories", "Basic analysis", "Community support"],
    },
    {
      id: "pro",
      name: "Pro plan",
      price: "$20",
      period: "/mth",
      features: [
        "Up to 20 repositories",
        "Advanced analytics",
        "Priority support",
        "API access",
      ],
      popular: true,
    },
    {
      id: "enterprise",
      name: "Enterprise plan",
      price: "$50",
      period: "/mth",
      features: [
        "Unlimited repositories",
        "Custom integrations",
        "Dedicated support",
        "SLA guarantee",
      ],
    },
  ];

  const invoices = [
    {
      id: "0012",
      date: "12 Apr 2025",
      plan: "Basic plan",
      amount: "USD $10.00",
    },
    {
      id: "0011",
      date: "12 Mar 2025",
      plan: "Basic plan",
      amount: "USD $10.00",
    },
    {
      id: "0010",
      date: "12 Feb 2025",
      plan: "Basic plan",
      amount: "USD $10.00",
    },
  ];

  return (
    <div className="relative max-w-5xl space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Plans & Billing</h2>
        <p className="text-muted-foreground">
          Manage your subscription and billing information
        </p>
      </div>

      <Separator className="dark:bg-white/5" />

      {/* Blurred Content */}
      <div className="relative">
        {/* Pricing Plans - Blurred */}
        <div className="pointer-events-none select-none space-y-8 opacity-50 blur-sm">
          <div className="space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Choose Your Plan
            </h3>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
              {plans.map((plan) => (
                <div
                  key={plan.id}
                  className={cn(
                    "relative flex flex-col rounded-xl border p-4 pb-0 shadow-sm backdrop-blur-sm transition-all duration-200",
                    currentPlan === plan.id
                      ? "border-primary bg-card ring-2 ring-primary/20 dark:border-primary dark:bg-[hsl(var(--surface-elevated))]/50"
                      : "border-border/50 bg-card hover:shadow-md dark:border-white/10 dark:bg-[hsl(var(--surface-elevated))]/30",
                  )}
                >
                  {plan.popular && (
                    <div className="absolute -top-2 left-1/2 -translate-x-1/2">
                      <span className="rounded-md bg-primary/90 px-2 py-0.5 text-[9px] font-semibold text-primary-foreground">
                        Popular
                      </span>
                    </div>
                  )}
                  <div className="flex-1 space-y-3">
                    <div>
                      <h4 className="text-base font-semibold">{plan.name}</h4>
                      <div className="mt-1 flex items-baseline gap-1">
                        <span className="text-2xl font-bold">{plan.price}</span>
                        <span className="text-xs text-muted-foreground">
                          {plan.period}
                        </span>
                      </div>
                    </div>
                    <ul className="space-y-1.5">
                      {plan.features.map((feature, index) => (
                        <li
                          key={index}
                          className="flex items-start gap-1.5 text-xs"
                        >
                          <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                          <span className="leading-tight text-muted-foreground">
                            {feature}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="pb-4 pt-3">
                    <Button
                      variant={currentPlan === plan.id ? "outline" : "default"}
                      className={cn(
                        "h-8 w-full text-xs",
                        currentPlan !== plan.id &&
                          "bg-[hsl(var(--secondary-accent))] hover:bg-[hsl(var(--secondary-accent))]/80 dark:bg-[hsl(var(--primary))] dark:hover:bg-[hsl(var(--primary))]/90",
                      )}
                      disabled={currentPlan === plan.id}
                      onClick={() => setCurrentPlan(plan.id)}
                    >
                      {currentPlan === plan.id
                        ? "Current plan"
                        : "Switch to this plan"}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Payment Method */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Payment Method
            </h3>
            <div className="rounded-xl border bg-card p-6 shadow-sm backdrop-blur-sm dark:border-white/10 dark:bg-[hsl(var(--surface-elevated))]/50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-md">
                    <CreditCard className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold">•••• •••• •••• 4242</h4>
                    <p className="text-sm text-muted-foreground">
                      Expires 12/2026 • Auto-renewal enabled
                    </p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="border-border hover:bg-[hsl(var(--secondary-accent))] hover:text-white dark:border-white/20 dark:hover:bg-[hsl(var(--primary))] dark:hover:text-white"
                >
                  Change
                </Button>
              </div>
            </div>
          </div>

          {/* Previous Invoices */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                Previous Invoices
              </h3>
              <button className="text-xs font-medium text-muted-foreground transition-colors duration-200 hover:text-primary">
                View all
              </button>
            </div>

            {/* Search and Sort */}
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-2 top-1/2 h-3 w-3 -translate-y-1/2 text-muted-foreground/70" />
                <Input
                  type="text"
                  placeholder="Search invoices..."
                  value={searchInvoice}
                  onChange={(e) => setSearchInvoice(e.target.value)}
                  className="h-8 rounded-md border-border/50 bg-muted/40 pl-7 pr-3 text-xs placeholder:text-muted-foreground/50 focus:border-primary/30 focus:bg-background"
                />
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  setSortOrder(sortOrder === "asc" ? "desc" : "asc")
                }
                className="h-8 gap-1.5 border-border px-3 text-xs hover:bg-[hsl(var(--secondary-accent))] hover:text-white dark:border-white/20 dark:hover:bg-[hsl(var(--primary))] dark:hover:text-white"
              >
                <ArrowUpDown className="h-3 w-3" />
                Date
              </Button>
            </div>
            <div className="overflow-hidden rounded-xl border bg-card shadow-sm backdrop-blur-sm dark:border-white/10 dark:bg-[hsl(var(--surface-elevated))]/50">
              <div className="divide-y dark:divide-white/5">
                {invoices.map((invoice) => (
                  <div
                    key={invoice.id}
                    className="flex items-center justify-between p-4 transition-colors hover:bg-muted/50 dark:hover:bg-white/5"
                  >
                    <div className="flex items-center gap-3">
                      <div>
                        <h4 className="text-sm font-semibold">
                          Invoice {invoice.id}
                        </h4>
                        <p className="text-xs text-muted-foreground">
                          {invoice.date}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm font-semibold">
                          {invoice.amount}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {invoice.plan}
                        </p>
                      </div>
                      <button className="flex h-8 w-8 items-center justify-center text-muted-foreground transition-colors duration-200 hover:text-primary">
                        <Download className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Coming Soon Overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="space-y-2 text-center">
            <h3 className="text-3xl font-bold text-foreground">Coming Soon</h3>
            <p className="text-sm text-muted-foreground">
              Plans & billing will be available soon
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function UsageContent() {
  return (
    <div className="relative max-w-3xl space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Usage</h2>
        <p className="text-muted-foreground">
          Monitor your usage and current limits
        </p>
      </div>

      <Separator className="dark:bg-white/5" />

      {/* Blurred Content */}
      <div className="relative">
        {/* Usage Metrics - Blurred */}
        <div className="pointer-events-none select-none space-y-4 opacity-50 blur-sm">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Current Usage
          </h3>
          <div className="space-y-4">
            <div className="rounded-xl border bg-card p-6 shadow-sm backdrop-blur-sm dark:border-white/10 dark:bg-[hsl(var(--surface-elevated))]/50">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold">API Calls</h4>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      Monthly API requests
                    </p>
                  </div>
                  <span className="text-lg font-bold">1,234 / 10,000</span>
                </div>
                <div className="h-3 overflow-hidden rounded-full bg-muted dark:bg-white/5">
                  <div
                    className="h-full rounded-full bg-primary transition-all duration-500"
                    style={{ width: "12.34%" }}
                  />
                </div>
                <p className="text-xs text-muted-foreground">12% used</p>
              </div>
            </div>

            <div className="rounded-xl border bg-card p-6 shadow-sm backdrop-blur-sm dark:border-white/10 dark:bg-[hsl(var(--surface-elevated))]/50">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold">Repositories</h4>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      Active repositories
                    </p>
                  </div>
                  <span className="text-lg font-bold">3 / 5</span>
                </div>
                <div className="h-3 overflow-hidden rounded-full bg-muted dark:bg-white/5">
                  <div
                    className="h-full rounded-full bg-primary transition-all duration-500"
                    style={{ width: "60%" }}
                  />
                </div>
                <p className="text-xs text-muted-foreground">60% used</p>
              </div>
            </div>
          </div>
        </div>

        {/* Coming Soon Overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="space-y-2 text-center">
            <h3 className="text-3xl font-bold text-foreground">Coming Soon</h3>
            <p className="text-sm text-muted-foreground">
              Usage metrics will be available soon
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
