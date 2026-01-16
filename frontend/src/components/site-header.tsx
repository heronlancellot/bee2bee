"use client";

import { useTheme } from "next-themes";
import {
  Search,
  Inbox,
  Moon,
  Sun,
  Command,
  X,
  Settings,
  LogOut,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { SidebarTrigger, useSidebar } from "@/components/ui/sidebar";
import Link from "next/link";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useRef, useState, useEffect } from "react";
import { SettingsDialog } from "@/components/settings-dialog";
import { useUserProfile } from "@/hooks/useUserProfile";
import { supabase } from "@/integrations/supabase/client";
import { useRouter } from "next/navigation";

export function SiteHeader() {
  const { theme, resolvedTheme, setTheme } = useTheme();
  const { state } = useSidebar();
  const { profile, loading: profileLoading } = useUserProfile();
  const router = useRouter();
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [searchValue, setSearchValue] = useState("");
  const [mounted, setMounted] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const currentTheme = mounted ? resolvedTheme || theme : "light";
  const isCollapsed = state === "collapsed";

  const logoSrc =
    currentTheme === "dark"
      ? isCollapsed
        ? "/branding/gradient_logo_icon.svg"
        : "/branding/gradient_logo_dark_theme_big.svg"
      : isCollapsed
        ? "/branding/gradient_logo_icon.svg"
        : "/branding/gradient_logo_light_theme_big.svg";

  // User data from profile
  const userDisplayName =
    profile?.full_name || profile?.github_username || "User";
  const userInitials = userDisplayName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .substring(0, 2);
  const userAvatar = profile?.avatar_url || "/avatars/shadcn.jpg";

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
      router.push("/login");
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  const handleThemeToggle = async () => {
    if (!buttonRef.current) return;

    const targetTheme = theme === "dark" ? "light" : "dark";

    // Check if View Transitions API is supported
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    if (!(document as any).startViewTransition) {
      setTheme(targetTheme);
      return;
    }

    // Get button position for the clip-path animation
    const rect = buttonRef.current.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    const endRadius =
      Math.hypot(
        Math.max(x, window.innerWidth - x),
        Math.max(y, window.innerHeight - y),
      ) * 2;

    // Create the transition
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const transition = (document as any).startViewTransition(async () => {
      setTheme(targetTheme);
    });

    try {
      await transition.ready;

      // Animate with clip-path from button center
      document.documentElement.animate(
        {
          clipPath: [
            `circle(0px at ${x}px ${y}px)`,
            `circle(${endRadius}px at ${x}px ${y}px)`,
          ],
        },
        {
          duration: 800,
          easing: "cubic-bezier(0.22, 1, 0.36, 1)",
          pseudoElement: "::view-transition-new(root)",
        },
      );
    } catch {
      // Fallback if transition fails - error intentionally ignored
    }
  };

  return (
    <header className="relative z-50 flex h-12 w-full shrink-0 items-center border-b border-border/50 bg-background dark:border-transparent dark:bg-[hsl(var(--header-background))] dark:shadow-[0_1px_0_0_hsl(var(--primary)/0.15),0_1px_8px_-2px_hsl(var(--primary)/0.2)]">
      {/* Logo Section - Fixed width matching sidebar */}
      <div
        className={`flex h-full items-center border-r border-border/50 transition-all duration-200 ease-linear dark:border-transparent dark:shadow-[1px_0_0_0_hsl(var(--primary)/0.15),1px_0_8px_-2px_hsl(var(--primary)/0.2)] ${isCollapsed ? "justify-center" : "px-4"}`}
        style={{
          width: isCollapsed
            ? "calc(var(--sidebar-width-icon) + 1rem)"
            : "var(--sidebar-width)",
        }}
      >
        <Link
          href="/"
          className="cursor-pointer transition-opacity duration-200 hover:opacity-80"
        >
          <img
            src={logoSrc}
            alt="Bee2Bee"
            className={`transition-all duration-200 ${isCollapsed ? "size-10" : "h-6 w-auto"}`}
          />
        </Link>
      </div>

      {/* Main Header Content */}
      <div className="flex h-full flex-1 items-center justify-between">
        {/* Left Section - Sidebar Toggle */}
        <div className="flex items-center px-3">
          <SidebarTrigger className="h-7 w-7 rounded-md transition-all duration-300 hover:bg-transparent [&>svg]:text-muted-foreground [&>svg]:transition-all [&>svg]:duration-300 [&>svg]:hover:text-primary [&>svg]:hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] [&>svg]:dark:text-primary/60 [&>svg]:dark:hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" />
        </div>

        {/* Right Section - Search + Notifications + Settings + Theme + User */}
        <div className="flex items-center gap-1.5 px-3">
          {/* Search Bar */}
          <div className="group relative">
            <Search className="pointer-events-none absolute left-2 top-1/2 h-3 w-3 -translate-y-1/2 text-muted-foreground/70 transition-colors duration-300 group-focus-within:text-primary" />
            <Input
              type="text"
              placeholder="Search..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="h-7 w-[160px] rounded-md border-border/50 bg-muted/40 pl-7 pr-12 text-xs transition-all duration-300 placeholder:text-muted-foreground/50 focus:w-[240px] focus:border-primary/30 focus:bg-background focus:shadow-[0_0_0_3px_hsl(var(--primary)/0.1)] [&::-webkit-search-cancel-button]:hidden [&::-webkit-search-decoration]:hidden"
            />
            {searchValue ? (
              <button
                onClick={() => setSearchValue("")}
                className="absolute right-1.5 top-1/2 inline-flex h-4 w-4 -translate-y-1/2 items-center justify-center rounded transition-colors duration-200 hover:bg-muted"
              >
                <X className="h-2.5 w-2.5 text-muted-foreground hover:text-foreground" />
              </button>
            ) : (
              <kbd className="pointer-events-none absolute right-1.5 top-1/2 inline-flex h-4 -translate-y-1/2 select-none items-center gap-0.5 rounded border bg-background px-1 font-mono text-[9px] font-medium text-muted-foreground/70 shadow-sm">
                <Command className="h-2 w-2" />K
              </kbd>
            )}
          </div>

          {/* Notification Dropdown */}
          {/* <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="relative h-7 w-7 rounded-md transition-all duration-300 hover:bg-transparent group"
            >
              <Inbox className="h-3.5 w-3.5 text-muted-foreground dark:text-primary/60 transition-all duration-300 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" />
              <span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-primary ring-1.5 ring-background shadow-[0_0_4px_hsl(var(--primary)/0.6)]" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-64">
            <DropdownMenuLabel className="text-xs">Notifications</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-xs py-2">
              <div className="flex flex-col gap-1">
                <p className="font-medium">New repository indexed</p>
                <p className="text-muted-foreground text-[10px]">nectar-frontend is ready</p>
              </div>
            </DropdownMenuItem>
            <DropdownMenuItem className="text-xs py-2">
              <div className="flex flex-col gap-1">
                <p className="font-medium">Agent completed task</p>
                <p className="text-muted-foreground text-[10px]">Code review finished</p>
              </div>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-xs justify-center text-primary">
              View all notifications
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu> */}

          {/* Theme Toggle */}
          <Button
            ref={buttonRef}
            variant="ghost"
            size="icon"
            onClick={handleThemeToggle}
            className="group relative h-7 w-7 overflow-hidden rounded-md transition-all duration-300 hover:bg-transparent"
          >
            <div className="relative h-3.5 w-3.5">
              <Sun className="absolute inset-0 h-3.5 w-3.5 rotate-0 scale-100 text-muted-foreground transition-all duration-500 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:rotate-90 dark:scale-0 dark:text-primary/60 dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" />
              <Moon className="absolute inset-0 h-3.5 w-3.5 rotate-90 scale-0 text-muted-foreground transition-all duration-500 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:rotate-0 dark:scale-100 dark:text-primary/60 dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" />
            </div>
          </Button>

          {/* User Info Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="ml-2 flex cursor-pointer items-center gap-2 border-l border-border/50 pl-2 transition-opacity duration-200 hover:opacity-80 dark:border-white/10">
                <Avatar className="h-6 w-6">
                  <AvatarImage src={userAvatar} alt={userDisplayName} />
                  <AvatarFallback className="bg-primary/10 text-[10px] font-semibold text-primary">
                    {profileLoading ? "..." : userInitials}
                  </AvatarFallback>
                </Avatar>
                <div className="flex flex-col">
                  <span className="text-xs font-semibold leading-none">
                    {profileLoading ? "Loading..." : userDisplayName}
                  </span>
                  <span className="mt-0.5 text-[10px] leading-none text-muted-foreground">
                    Free Plan
                  </span>
                </div>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuLabel className="text-xs">Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="cursor-pointer py-2 text-xs"
                onClick={() => setSettingsOpen(true)}
              >
                <Settings className="mr-2 h-3.5 w-3.5" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="cursor-pointer py-2 text-xs text-destructive focus:text-destructive"
                onClick={handleLogout}
              >
                <LogOut className="mr-2 h-3.5 w-3.5" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <SettingsDialog open={settingsOpen} onOpenChange={setSettingsOpen} />
    </header>
  );
}
