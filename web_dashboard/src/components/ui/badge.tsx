import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded px-2 py-0.5 text-[0.62rem] font-bold uppercase tracking-wider border",
  {
    variants: {
      variant: {
        default: "border-accentCyan/30 bg-accentCyan/10 text-accentCyan",
        gold: "border-accentGold/30 bg-accentGold/10 text-accentGold",
        green: "border-successGreen/30 bg-successGreen/10 text-successGreen",
        amber: "border-warningAmber/30 bg-warningAmber/10 text-warningAmber",
        red: "border-riskRed/30 bg-riskRed/10 text-riskRed",
        purple: "border-mutedPurple/30 bg-mutedPurple/10 text-mutedPurple",
        muted: "border-border bg-surfaceAlt/50 text-textSecondary",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
