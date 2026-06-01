"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import { motion } from "framer-motion";
import { Activity, Database, Globe2, LayoutDashboard, LineChart, Shield, Coins } from "lucide-react";
import { cn } from "@/lib/utils";
import { withBasePath } from "@/lib/base-path";

const NAV = [
  { href: "/", label: "Home", icon: LayoutDashboard },
  { href: "/command-center", label: "Command Center", icon: Activity },
  { href: "/value-flow", label: "Value Flow", icon: Globe2 },
  { href: "/value-survival", label: "Value Survival", icon: LineChart },
  { href: "/settlement", label: "Settlement", icon: Database },
  { href: "/stablecoins", label: "Stablecoins", icon: Coins },
  { href: "/data-lake", label: "Data Lake", icon: Database },
  { href: "/audit", label: "Audit", icon: Shield },
];

export function Shell({
  children,
  title,
  subtitle,
  wide = false,
}: {
  children: ReactNode;
  title: string;
  subtitle?: string;
  wide?: boolean;
}) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen grid-bg">
      <header className="border-b border-border/80 bg-surface/70 backdrop-blur-xl sticky top-0 z-50">
        <div className={cn("mx-auto px-4 py-3", wide ? "max-w-[1400px]" : "max-w-7xl")}>
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <a
                href="/br3n-macro-lab/index.html"
                className="inline-block mb-2 opacity-90 hover:opacity-100 transition-opacity"
              >
                <img
                  src={withBasePath("/assets/brand/bfi-logo-horizontal-inverse.svg")}
                  alt="Bowers Frontier Institute"
                  className="h-7 w-auto"
                />
              </a>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-[0.62rem] uppercase tracking-[0.28em] text-accentGold font-semibold"
              >
                BR3N Macro Lab · Division
              </motion.div>
              <h1 className="text-lg md:text-xl font-semibold text-textPrimary">{title}</h1>
              {subtitle && <p className="text-xs md:text-sm text-textSecondary mt-0.5">{subtitle}</p>}
            </div>
            <nav className="flex flex-wrap gap-1.5">
              {NAV.map(({ href, label, icon: Icon }) => {
                const active = pathname === href;
                return (
                  <Link
                    key={href}
                    href={href}
                    className={cn(
                      "inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-[0.68rem] font-medium border transition-all",
                      active
                        ? "bg-accentCyan/12 border-accentCyan/35 text-accentCyan shadow-[0_0_20px_rgba(56,189,248,0.12)]"
                        : "border-transparent text-textSecondary hover:text-textPrimary hover:border-border/80 hover:bg-surfaceAlt/50"
                    )}
                  >
                    <Icon size={12} />
                    {label}
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </header>
      <main className={cn("mx-auto px-4 py-6 space-y-6", wide ? "max-w-[1400px]" : "max-w-7xl")}>
        {children}
      </main>
      <footer className="border-t border-border/60 py-5 text-center text-[0.65rem] text-textSecondary tracking-wide">
        Research only · Not investment advice · Python data engine · React visualization layer
      </footer>
    </div>
  );
}
