"use client"

import {
  CreditCardIcon,
  LogOutIcon,
  MoreVerticalIcon,
  UserCircleIcon,
} from "lucide-react"

import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"

export function NavUser({
  user,
}: {
  user: {
    name: string
    email: string
    avatar: string
  }
}) {
  const { isMobile } = useSidebar()

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="group/user transition-all duration-300 hover:bg-muted/50 data-[state=open]:bg-muted border border-transparent hover:border-border"
            >
              <Avatar className="h-8 w-8 rounded-lg grayscale transition-all duration-300 group-hover/user:grayscale-0 group-hover/user:scale-105">
                <AvatarImage src={user.avatar} alt={user.name} />
                <AvatarFallback className="rounded-lg bg-muted text-foreground">CN</AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-medium transition-colors duration-300 group-hover/user:text-foreground">{user.name}</span>
                <span className="truncate text-xs text-muted-foreground transition-colors duration-300 group-hover/user:text-foreground/70">
                  {user.email}
                </span>
              </div>
              <MoreVerticalIcon className="ml-auto size-4 rotate-90" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-[--radix-dropdown-menu-trigger-width] min-w-44 rounded-lg border shadow-lg p-1"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuGroup>
              <DropdownMenuItem className="group/item cursor-pointer rounded-md text-xs font-medium transition-all duration-200 px-2 py-1.5">
                <UserCircleIcon className="size-3.5 transition-transform duration-200 group-hover/item:scale-105" />
                Account
              </DropdownMenuItem>
              <DropdownMenuItem className="group/item cursor-pointer rounded-md text-xs font-medium transition-all duration-200 px-2 py-1.5">
                <CreditCardIcon className="size-3.5 transition-transform duration-200 group-hover/item:scale-105" />
                Billing
              </DropdownMenuItem>
              <DropdownMenuSeparator className="my-1" />
              <DropdownMenuItem className="group/item cursor-pointer rounded-md text-xs font-medium text-red-600 transition-all duration-200 hover:!bg-red-100 hover:!text-red-700 dark:text-red-500 dark:hover:!bg-red-950/40 dark:hover:!text-red-400 px-2 py-1.5">
                <LogOutIcon className="size-3.5 transition-transform duration-200 group-hover/item:scale-105" />
                Log out
              </DropdownMenuItem>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
