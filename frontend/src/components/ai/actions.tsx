'use client';

import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import type { ComponentProps } from 'react';

export type ActionsProps = ComponentProps<'div'>;

export const Actions = ({ className, children, ...props }: ActionsProps) => (
  <div className={cn('flex items-center gap-1', className)} {...props}>
    {children}
  </div>
);

export type ActionProps = ComponentProps<'button'> & {
  tooltip?: string;
  label?: string;
};

export const Action = ({
  tooltip,
  children,
  label,
  className,
  ...props
}: ActionProps) => {
  const button = (
    <button
      className={cn(
        'h-6 w-6 p-0 flex items-center justify-center text-muted-foreground transition-all duration-300 hover:bg-transparent [&>svg]:transition-all [&>svg]:duration-300 [&>svg]:hover:text-primary [&>svg]:hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] [&>svg]:dark:hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]',
        className
      )}
      type="button"
      {...props}
    >
      {children}
      <span className="sr-only">{label || tooltip}</span>
    </button>
  );

  if (tooltip) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>{button}</TooltipTrigger>
          <TooltipContent>
            <p>{tooltip}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return button;
};
