"use client";

import * as React from "react";
import dynamic from "next/dynamic";
import * as echarts from "echarts";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

type Props = {
  option: Record<string, unknown>;
  height?: number | string;
  className?: string;
  onChartReady?: (chart: echarts.ECharts) => void;
};

export function EChart({ option, height = 380, className, onChartReady }: Props) {
  return (
    <ReactECharts
      echarts={echarts}
      option={option}
      style={{ height, width: "100%" }}
      className={className}
      onChartReady={onChartReady}
      notMerge
      lazyUpdate
    />
  );
}
