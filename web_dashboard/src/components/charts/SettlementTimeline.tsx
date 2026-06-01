"use client";

import { useEffect, useState } from "react";
import { EChart } from "@/components/charts/EChart";
import { settlementTimelineOption } from "@/lib/charts/options";
import type { TimelineStage } from "@/lib/types";

export function SettlementTimelineAnimator({ stages }: { stages: TimelineStage[] }) {
  const [frame, setFrame] = useState(1);

  useEffect(() => {
    if (stages.length <= 1) return;
    const id = setInterval(() => {
      setFrame((f) => (f >= stages.length ? 1 : f + 1));
    }, 1800);
    return () => clearInterval(id);
  }, [stages.length]);

  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-3">
        {stages.map((s, i) => (
          <button
            key={s.stage}
            type="button"
            onClick={() => setFrame(i + 1)}
            className={`text-[0.65rem] px-2 py-1 rounded border transition ${
              i < frame
                ? "border-accentCyan/40 bg-accentCyan/10 text-accentCyan"
                : "border-border text-textSecondary"
            }`}
          >
            {s.stage}
          </button>
        ))}
      </div>
      <EChart option={settlementTimelineOption(stages, frame)} height={360} />
    </div>
  );
}
