"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Database, Globe2, LineChart, Shield, Coins, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const modules = [
  { icon: LineChart, label: "Value Survival Index", href: "/value-survival", tag: "VSI" },
  { icon: Globe2, label: "Global Value Flow", href: "/value-flow", tag: "MAP" },
  { icon: Database, label: "Settlement Economics", href: "/settlement", tag: "SEL" },
  { icon: Coins, label: "Stablecoin Windows", href: "/stablecoins", tag: "SC" },
  { icon: Shield, label: "Audit & Quality", href: "/audit", tag: "QA" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen grid-bg flex flex-col relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(56,189,248,0.08),transparent_45%)]" />
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-accentGold/5 blur-[120px] pulse-glow" />

      <div className="flex-1 flex flex-col items-center justify-center px-4 py-20 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="max-w-4xl"
        >
          <Badge variant="gold" className="mb-5">
            <Sparkles size={10} className="mr-1 inline" /> Bowers Frontier Macro Labs
          </Badge>
          <h1 className="text-4xl md:text-6xl font-semibold text-textPrimary leading-[1.1] tracking-tight">
            Domain-specific AI for
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-accentCyan to-accentGold">
              FX &amp; Treasury Intelligence
            </span>
          </h1>
          <p className="mt-5 text-textSecondary text-base md:text-lg max-w-2xl mx-auto leading-relaxed">
            Research systems combining market data, macro signals, corridor analytics, model evaluation,
            and AI-assisted reporting. Value Survival · Settlement Economics · Stablecoin Finality · Data Lineage.
          </p>
          <div className="mt-8 flex flex-wrap gap-3 justify-center">
            <Button asChild variant="gold" size="lg">
              <Link href="/command-center">
                Enter Command Center <ArrowRight size={16} />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/value-flow">Global Value Flow Map</Link>
            </Button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mt-16 max-w-5xl w-full"
        >
          {modules.map(({ icon: Icon, label, href, tag }, i) => (
            <motion.div
              key={href}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.06 }}
            >
              <Link
                href={href}
                className="group block rounded-xl border border-border/70 bg-surface/60 backdrop-blur-xl p-4 text-left hover:border-accentCyan/35 transition-all hover:shadow-[0_8px_32px_rgba(56,189,248,0.08)]"
              >
                <div className="flex items-center justify-between mb-3">
                  <Icon className="text-accentCyan group-hover:scale-110 transition-transform" size={20} />
                  <span className="text-[0.6rem] font-mono text-textSecondary">{tag}</span>
                </div>
                <div className="text-sm font-medium text-textPrimary">{label}</div>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}
