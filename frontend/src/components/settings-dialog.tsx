"use client"

import * as React from "react"
import { Settings, Github, Palette, CreditCard, BarChart3 } from "lucide-react"
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
          icon: Palette,
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
      <DialogContent className="max-w-5xl h-[700px] p-0 gap-0 bg-background dark:bg-[#0A0A0A]">
        <div className="flex h-full">
          {/* Sidebar */}
          <div className="w-64 border-r dark:border-white/5 bg-muted/30 dark:bg-[#0D0D0D] p-4 flex flex-col gap-5">
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
                            ? "bg-background dark:bg-[#1A1A1A] text-foreground shadow-sm"
                            : "text-muted-foreground hover:text-foreground hover:bg-background/50 dark:hover:bg-[#151515]"
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
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-1">GitHub</h3>
        <p className="text-sm text-muted-foreground">
          Connect your GitHub account to sync and analyze your repositories
        </p>
      </div>

      <Separator className="dark:bg-white/5" />

      {/* GitHub Connection Status */}
      <div className="flex items-center justify-between p-4 rounded-lg border dark:border-white/5 bg-card dark:bg-[#0D0D0D]">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#24292e] dark:bg-[#1A1A1A]">
            <Github className="h-5 w-5 text-white" />
          </div>
          <div>
            <h4 className="font-semibold text-sm">GitHub Account</h4>
            <p className="text-xs text-muted-foreground">
              {githubConnected ? "Connected and syncing" : "Not connected"}
            </p>
          </div>
        </div>
        {githubConnected ? (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setGithubConnected(false)}
            className="dark:border-white/10"
          >
            Disconnect
          </Button>
        ) : (
          <Button
            size="sm"
            onClick={() => setGithubConnected(true)}
          >
            Connect
          </Button>
        )}
      </div>

      {/* Quick Actions (only show when connected) */}
      {githubConnected && (
        <Button variant="outline" size="sm" className="dark:border-white/10">
          Manage Repositories
        </Button>
      )}
    </div>
  )
}

function PreferencesContent() {
  const [notifications, setNotifications] = React.useState(true)
  const [autoSync, setAutoSync] = React.useState(true)

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-1">Preferences</h3>
        <p className="text-sm text-muted-foreground">
          Customize your experience
        </p>
      </div>

      <Separator className="dark:bg-white/5" />

      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 rounded-lg border dark:border-white/5 bg-card dark:bg-[#0D0D0D]">
          <div className="space-y-0.5">
            <Label htmlFor="notifications" className="text-sm font-medium">
              Notifications
            </Label>
            <p className="text-xs text-muted-foreground">
              Receive notifications about your repositories
            </p>
          </div>
          <Switch
            id="notifications"
            checked={notifications}
            onCheckedChange={setNotifications}
          />
        </div>

        <div className="flex items-center justify-between p-4 rounded-lg border dark:border-white/5 bg-card dark:bg-[#0D0D0D]">
          <div className="space-y-0.5">
            <Label htmlFor="auto-sync" className="text-sm font-medium">
              Auto Sync
            </Label>
            <p className="text-xs text-muted-foreground">
              Automatically sync repositories
            </p>
          </div>
          <Switch
            id="auto-sync"
            checked={autoSync}
            onCheckedChange={setAutoSync}
          />
        </div>
      </div>
    </div>
  )
}

function PlansContent() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-1">Plans & Billing</h3>
        <p className="text-sm text-muted-foreground">
          Manage your subscription and billing
        </p>
      </div>

      <Separator className="dark:bg-white/5" />

      <div className="p-6 rounded-lg border dark:border-white/5 bg-card dark:bg-[#0D0D0D]">
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold mb-1">Current Plan</h4>
            <p className="text-2xl font-bold text-primary">Free Plan</p>
          </div>
          <p className="text-sm text-muted-foreground">
            Upgrade to unlock more features and increase your limits
          </p>
          <Button className="w-full sm:w-auto">
            Upgrade Plan
          </Button>
        </div>
      </div>
    </div>
  )
}

function UsageContent() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-1">Usage</h3>
        <p className="text-sm text-muted-foreground">
          Monitor your usage and limits
        </p>
      </div>

      <Separator className="dark:bg-white/5" />

      <div className="space-y-4">
        <div className="p-4 rounded-lg border dark:border-white/5 bg-card dark:bg-[#0D0D0D]">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">API Calls</span>
              <span className="font-medium">1,234 / 10,000</span>
            </div>
            <div className="h-2 rounded-full bg-muted dark:bg-[#1A1A1A] overflow-hidden">
              <div className="h-full bg-primary rounded-full" style={{ width: "12.34%" }} />
            </div>
          </div>
        </div>

        <div className="p-4 rounded-lg border dark:border-white/5 bg-card dark:bg-[#0D0D0D]">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Repositories</span>
              <span className="font-medium">3 / 5</span>
            </div>
            <div className="h-2 rounded-full bg-muted dark:bg-[#1A1A1A] overflow-hidden">
              <div className="h-full bg-primary rounded-full" style={{ width: "60%" }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
