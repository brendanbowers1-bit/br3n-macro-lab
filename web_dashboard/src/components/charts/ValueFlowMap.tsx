"use client";

import { useEffect, useState } from "react";
import * as echarts from "echarts";
import { EChart } from "@/components/charts/EChart";
import { valueFlowGlobeOption } from "@/lib/charts/options";
import type { ValueFlowLine } from "@/lib/types";

const WORLD_URL = "https://echarts.apache.org/examples/data/asset/geo/world.json";

export function ValueFlowMap({ lines, height = 520 }: { lines: ValueFlowLine[]; height?: number }) {
  const [ready, setReady] = useState(false);
  const [option, setOption] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(WORLD_URL);
        const geo = await res.json();
        if (cancelled) return;
        echarts.registerMap("world", geo);
        setOption(valueFlowGlobeOption(lines));
        setReady(true);
      } catch {
        if (!cancelled) setReady(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [lines]);

  if (!ready || !option) {
    return (
      <div className="flex items-center justify-center text-textSecondary text-sm" style={{ height }}>
        Initializing global value flow map…
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(56,189,248,0.06),transparent_70%)] pointer-events-none z-10" />
      <EChart option={option} height={height} />
    </div>
  );
}
