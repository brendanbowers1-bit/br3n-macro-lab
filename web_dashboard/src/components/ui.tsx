"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

type Props = {
  label: string;
  value: string;
  sub?: string;
  tone?: "cyan" | "gold" | "red" | "green" | "amber";
};

const toneMap = {
  cyan: "text-accentCyan border-accentCyan/30",
  gold: "text-accentGold border-accentGold/30",
  red: "text-riskRed border-riskRed/30",
  green: "text-successGreen border-successGreen/30",
  amber: "text-warningAmber border-warningAmber/30",
};

export function KpiCard({ label, value, sub, tone = "cyan" }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-4 min-h-[96px]"
    >
      <div className="text-[0.68rem] uppercase tracking-widest text-textSecondary">{label}</div>
      <div className="font-mono text-2xl font-semibold mt-1 text-textPrimary">{value}</div>
      {sub && (
        <div className={`text-xs mt-2 inline-block px-2 py-0.5 rounded border ${toneMap[tone]}`}>
          {sub}
        </div>
      )}
    </motion.div>
  );
}

export function ChartCard({ title, caption, children }: { title: string; caption?: string; children: ReactNode }) {
  return (
    <div className="glass-card p-4">
      <h3 className="text-sm font-semibold text-textPrimary">{title}</h3>
      {caption && <p className="text-xs text-textSecondary mt-1 mb-3">{caption}</p>}
      {children}
    </div>
  );
}

export function WarningBanner({ children }: { children: ReactNode }) {
  return (
    <div className="border-l-4 border-warningAmber bg-warningAmber/10 rounded-r-lg px-4 py-3 text-sm text-textSecondary">
      {children}
    </div>
  );
}
