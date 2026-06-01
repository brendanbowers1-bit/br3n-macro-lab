"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import { cn } from "@/lib/utils";

type Tone = "cyan" | "gold" | "red" | "green" | "amber" | "purple";

const toneStyles: Record<Tone, string> = {
  cyan: "from-accentCyan/20 to-transparent border-accentCyan/25 text-accentCyan",
  gold: "from-accentGold/20 to-transparent border-accentGold/25 text-accentGold",
  red: "from-riskRed/20 to-transparent border-riskRed/25 text-riskRed",
  green: "from-successGreen/20 to-transparent border-successGreen/25 text-successGreen",
  amber: "from-warningAmber/20 to-transparent border-warningAmber/25 text-warningAmber",
  purple: "from-mutedPurple/20 to-transparent border-mutedPurple/25 text-mutedPurple",
};

export function AnimatedKpi({
  label,
  value,
  sub,
  tone = "cyan",
  delay = 0,
}: {
  label: string;
  value: string;
  sub?: string;
  tone?: Tone;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.45, delay, ease: [0.22, 1, 0.36, 1] }}
      className={cn(
        "relative overflow-hidden rounded-xl border bg-gradient-to-br p-4 min-h-[104px]",
        "backdrop-blur-xl shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]",
        toneStyles[tone]
      )}
    >
      <div className="absolute inset-0 scanline opacity-[0.03] pointer-events-none" />
      <div className="text-[0.62rem] uppercase tracking-[0.22em] text-textSecondary">{label}</div>
      <div className="font-mono text-2xl md:text-3xl font-semibold mt-1 text-textPrimary tabular-nums">{value}</div>
      {sub && <div className="text-[0.68rem] mt-2 text-textSecondary font-mono">{sub}</div>}
    </motion.div>
  );
}

export function ChartPanel({
  title,
  caption,
  badge,
  children,
  className,
}: {
  title: string;
  caption?: string;
  badge?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={cn(
        "rounded-xl border border-border/80 bg-surface/70 backdrop-blur-xl",
        "shadow-[0_12px_40px_rgba(0,0,0,0.35)] overflow-hidden",
        className
      )}
    >
      <div className="flex items-start justify-between gap-3 px-4 pt-4 pb-2 border-b border-border/50">
        <div>
          <h3 className="text-sm font-semibold text-textPrimary tracking-tight">{title}</h3>
          {caption && <p className="text-xs text-textSecondary mt-0.5 leading-relaxed">{caption}</p>}
        </div>
        {badge}
      </div>
      <div className="p-3">{children}</div>
    </motion.div>
  );
}

export function CredibilityBanner({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex gap-3 rounded-lg border border-warningAmber/30 bg-warningAmber/5 px-4 py-3 text-xs text-textSecondary leading-relaxed"
    >
      <span className="text-warningAmber font-bold shrink-0">⚠</span>
      <div>{children}</div>
    </motion.div>
  );
}

export function LoadingPulse({ message = "Syncing research payload…" }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4">
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="w-2 h-2 rounded-full bg-accentCyan"
            animate={{ opacity: [0.3, 1, 0.3], scale: [0.8, 1.1, 0.8] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.15 }}
          />
        ))}
      </div>
      <p className="text-sm text-textSecondary font-mono">{message}</p>
      <p className="text-xs text-textSecondary/70">
        Run: <code className="text-accentCyan">python scripts/export_dashboard_api.py</code>
      </p>
    </div>
  );
}

export function CinematicHero({ children }: { children: ReactNode }) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-border/60 bg-surface/40 p-6 md:p-8">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(56,189,248,0.08),transparent_55%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(212,175,55,0.06),transparent_50%)]" />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
