"use client"

import * as React from "react"
import { Settings, Github, Settings2, CreditCard, BarChart3, Check, Download, Search, ArrowUpDown } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"

type SettingsSection = "github" | "preferences" | "plans" | "usage"

interface SettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface SidebarSection {
  label: string
  items: {
    id: SettingsSection
    label: string
    icon: any
  }[]
}

export function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
  const [activeSection, setActiveSection] = React.useState<SettingsSection>("github")

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
  ]

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl h-[85vh] max-h-[700px] p-0 gap-0 bg-background dark:bg-[hsl(var(--surface-elevated))]">
        <div className="flex h-full overflow-hidden">
          {/* Sidebar */}
          <div className="w-64 border-r dark:border-white/5 bg-muted/30 dark:bg-[hsl(var(--surface-elevated))] p-4 flex flex-col gap-5 overflow-y-auto">
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
                    const Icon = item.icon
                    return (
                      <button
                        key={item.id}
                        onClick={() => setActiveSection(item.id)}
                        className={cn(
                          "flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm transition-all duration-200",
                          activeSection === item.id
                            ? "bg-secondary dark:bg-[#1A1A1A] text-foreground shadow-sm font-semibold border border-border/50 dark:border-white/10"
                            : "text-muted-foreground hover:text-foreground hover:bg-muted/40 dark:hover:bg-[#151515]"
                        )}
                      >
                        <Icon className="h-4 w-4 shrink-0" />
                        <span className="font-medium">{item.label}</span>
                      </button>
                    )
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
  )
}

function IntegrationsContent() {
  const [githubConnected, setGithubConnected] = React.useState(true)

  return (
    <div className="space-y-8 max-w-3xl">
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
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Connection
        </h3>
        <div className="flex items-center justify-between p-6 rounded-xl border dark:border-white/10 bg-card dark:bg-[hsl(var(--surface-elevated))]/50 backdrop-blur-sm shadow-sm hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#24292e] dark:bg-white border dark:border-white/10 shadow-md">
              <Github className="h-6 w-6 text-white dark:text-[#24292e]" />
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
              onClick={() => setGithubConnected(false)}
              className="border-border hover:bg-[hsl(var(--secondary-accent))] hover:text-white dark:border-white/20 dark:hover:bg-[hsl(var(--primary))] dark:hover:text-white"
            >
              Disconnect
            </Button>
          ) : (
            <Button
              onClick={() => setGithubConnected(true)}
              className="bg-[hsl(var(--secondary-accent))] hover:bg-[hsl(var(--secondary-accent))]/80 dark:bg-[hsl(var(--primary))] dark:hover:bg-[hsl(var(--primary))]/90"
            >
              Connect GitHub
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

function PreferencesContent() {
  const [notifications, setNotifications] = React.useState(true)

  return (
    <div className="space-y-8 max-w-3xl">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Preferences</h2>
        <p className="text-muted-foreground">
          Customize your experience and notification settings
        </p>
      </div>

      <Separator className="dark:bg-white/5" />

      {/* Notifications Section */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Notifications
        </h3>
        <div className="flex items-center justify-between p-6 rounded-xl border dark:border-white/10 bg-card dark:bg-[hsl(var(--surface-elevated))]/50 backdrop-blur-sm shadow-sm hover:shadow-md transition-shadow duration-200">
          <div className="space-y-1">
            <Label htmlFor="notifications" className="text-base font-semibold cursor-pointer">
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
    </div>
  )
}

function PlansContent() {
  const [currentPlan, setCurrentPlan] = React.useState("free")
  const [searchInvoice, setSearchInvoice] = React.useState("")
  const [sortOrder, setSortOrder] = React.useState<"asc" | "desc">("desc")

  const plans = [
    {
      id: "free",
      name: "Free plan",
      price: "$0",
      period: "/mth",
      features: [
        "Up to 3 repositories",
        "Basic analysis",
        "Community support",
      ],
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
  ]

  const invoices = [
    { id: "0012", date: "12 Apr 2025", plan: "Basic plan", amount: "USD $10.00" },
    { id: "0011", date: "12 Mar 2025", plan: "Basic plan", amount: "USD $10.00" },
    { id: "0010", date: "12 Feb 2025", plan: "Basic plan", amount: "USD $10.00" },
  ]

  return (
    <div className="space-y-8 max-w-5xl">
      {/* Header */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Plans & Billing</h2>
        <p className="text-muted-foreground">
          Manage your subscription and billing information
        </p>
      </div>

      <Separator className="dark:bg-white/5" />

      {/* Pricing Plans */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Choose Your Plan
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={cn(
                "relative p-4 pb-0 rounded-xl border backdrop-blur-sm shadow-sm transition-all duration-200 flex flex-col",
                currentPlan === plan.id
                  ? "border-primary dark:border-primary bg-card dark:bg-[hsl(var(--surface-elevated))]/50 ring-2 ring-primary/20"
                  : "border-border/50 dark:border-white/10 bg-card dark:bg-[hsl(var(--surface-elevated))]/30 hover:shadow-md"
              )}
            >
              {plan.popular && (
                <div className="absolute -top-2 left-1/2 -translate-x-1/2">
                  <span className="px-2 py-0.5 text-[9px] font-semibold bg-primary/90 text-primary-foreground rounded-md">
                    Popular
                  </span>
                </div>
              )}
              <div className="space-y-3 flex-1">
                <div>
                  <h4 className="font-semibold text-base">{plan.name}</h4>
                  <div className="flex items-baseline gap-1 mt-1">
                    <span className="text-2xl font-bold">{plan.price}</span>
                    <span className="text-muted-foreground text-xs">{plan.period}</span>
                  </div>
                </div>
                <ul className="space-y-1.5">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-1.5 text-xs">
                      <Check className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
                      <span className="text-muted-foreground leading-tight">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="pt-3 pb-4">
                <Button
                  variant={currentPlan === plan.id ? "outline" : "default"}
                  className={cn(
                    "w-full h-8 text-xs",
                    currentPlan !== plan.id && "bg-[hsl(var(--secondary-accent))] hover:bg-[hsl(var(--secondary-accent))]/80 dark:bg-[hsl(var(--primary))] dark:hover:bg-[hsl(var(--primary))]/90"
                  )}
                  disabled={currentPlan === plan.id}
                  onClick={() => setCurrentPlan(plan.id)}
                >
                  {currentPlan === plan.id ? "Current plan" : "Switch to this plan"}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Payment Method */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Payment Method
        </h3>
        <div className="p-6 rounded-xl border dark:border-white/10 bg-card dark:bg-[hsl(var(--surface-elevated))]/50 backdrop-blur-sm shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-md">
                <CreditCard className="h-6 w-6 text-white" />
              </div>
              <div>
                <h4 className="font-semibold">•••• •••• •••• 4242</h4>
                <p className="text-sm text-muted-foreground">Expires 12/2026 • Auto-renewal enabled</p>
              </div>
            </div>
            <Button variant="outline" size="sm" className="border-border hover:bg-[hsl(var(--secondary-accent))] hover:text-white dark:border-white/20 dark:hover:bg-[hsl(var(--primary))] dark:hover:text-white">
              Change
            </Button>
          </div>
        </div>
      </div>

      {/* Previous Invoices */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            Previous Invoices
          </h3>
          <button className="text-xs text-muted-foreground hover:text-primary transition-colors duration-200 font-medium">
            View all
          </button>
        </div>

        {/* Search and Sort */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-2 top-1/2 h-3 w-3 -translate-y-1/2 text-muted-foreground/70 pointer-events-none" />
            <Input
              type="text"
              placeholder="Search invoices..."
              value={searchInvoice}
              onChange={(e) => setSearchInvoice(e.target.value)}
              className="h-8 pl-7 pr-3 text-xs rounded-md bg-muted/40 border-border/50 focus:bg-background focus:border-primary/30 placeholder:text-muted-foreground/50"
            />
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
            className="h-8 px-3 text-xs border-border hover:bg-[hsl(var(--secondary-accent))] hover:text-white dark:border-white/20 dark:hover:bg-[hsl(var(--primary))] dark:hover:text-white gap-1.5"
          >
            <ArrowUpDown className="h-3 w-3" />
            Date
          </Button>
        </div>
        <div className="rounded-xl border dark:border-white/10 bg-card dark:bg-[hsl(var(--surface-elevated))]/50 backdrop-blur-sm shadow-sm overflow-hidden">
          <div className="divide-y dark:divide-white/5">
            {invoices.map((invoice) => (
              <div
                key={invoice.id}
                className="flex items-center justify-between p-4 hover:bg-muted/50 dark:hover:bg-white/5 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div>
                    <h4 className="font-semibold text-sm">Invoice {invoice.id}</h4>
                    <p className="text-xs text-muted-foreground">{invoice.date}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm font-semibold">{invoice.amount}</p>
                    <p className="text-xs text-muted-foreground">{invoice.plan}</p>
                  </div>
                  <button className="h-8 w-8 flex items-center justify-center text-muted-foreground hover:text-primary transition-colors duration-200">
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function UsageContent() {
  return (
    <div className="space-y-8 max-w-3xl relative">
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
        <div className="space-y-4 blur-sm pointer-events-none select-none opacity-50">
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            Current Usage
          </h3>
          <div className="space-y-4">
            <div className="p-6 rounded-xl border dark:border-white/10 bg-card dark:bg-[hsl(var(--surface-elevated))]/50 backdrop-blur-sm shadow-sm">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold">API Calls</h4>
                    <p className="text-xs text-muted-foreground mt-0.5">Monthly API requests</p>
                  </div>
                  <span className="text-lg font-bold">1,234 / 10,000</span>
                </div>
                <div className="h-3 rounded-full bg-muted dark:bg-white/5 overflow-hidden">
                  <div className="h-full bg-primary rounded-full transition-all duration-500" style={{ width: "12.34%" }} />
                </div>
                <p className="text-xs text-muted-foreground">12% used</p>
              </div>
            </div>

            <div className="p-6 rounded-xl border dark:border-white/10 bg-card dark:bg-[hsl(var(--surface-elevated))]/50 backdrop-blur-sm shadow-sm">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold">Repositories</h4>
                    <p className="text-xs text-muted-foreground mt-0.5">Active repositories</p>
                  </div>
                  <span className="text-lg font-bold">3 / 5</span>
                </div>
                <div className="h-3 rounded-full bg-muted dark:bg-white/5 overflow-hidden">
                  <div className="h-full bg-primary rounded-full transition-all duration-500" style={{ width: "60%" }} />
                </div>
                <p className="text-xs text-muted-foreground">60% used</p>
              </div>
            </div>
          </div>
        </div>

        {/* Coming Soon Overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center space-y-2">
            <h3 className="text-3xl font-bold text-foreground">Coming Soon</h3>
            <p className="text-sm text-muted-foreground">Usage metrics will be available soon</p>
          </div>
        </div>
      </div>
    </div>
  )
}
