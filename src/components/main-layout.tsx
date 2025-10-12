"use client"

import * as React from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { SiteHeader } from "@/components/site-header"

interface MainLayoutProps {
  children: React.ReactNode
  showHeader?: boolean
}

export function MainLayout({ children, showHeader = true }: MainLayoutProps) {
  return (
    <SidebarProvider>
      <AppSidebar variant="inset" />
      <SidebarInset className="rounded-xl border border-border/40 bg-background shadow-sm overflow-hidden">
        {showHeader && <SiteHeader />}
        <div className="flex flex-1 flex-col overflow-auto">
          {children}
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
