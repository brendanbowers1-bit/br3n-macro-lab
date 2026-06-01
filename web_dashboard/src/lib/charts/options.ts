import type { SankeyPayload, ValueFlowLine, LineageGraph, TimelineStage } from "../types";
import { C, baseGrid } from "./theme";

export function sankeyOption(payload: SankeyPayload) {
  return {
    backgroundColor: "transparent",
    tooltip: { trigger: "item" },
    series: [{
      type: "sankey",
      layout: "none",
      emphasis: { focus: "adjacency" },
      nodeAlign: "left",
      lineStyle: { color: "gradient", curveness: 0.5, opacity: 0.45 },
      itemStyle: { borderWidth: 0 },
      label: { color: C.muted, fontSize: 10, fontFamily: "JetBrains Mono" },
      data: payload.nodes.map((n, i) => ({
        ...n,
        itemStyle: {
          color: i === 0 ? C.gold : i === payload.nodes.length - 1 ? C.green : C.cyan,
        },
      })),
      links: payload.links,
      left: "4%",
      right: "12%",
      top: "4%",
      bottom: "4%",
    }],
  };
}

export function valueFlowGlobeOption(lines: ValueFlowLine[]) {
  const data = lines.map((l) => ({
    coords: l.coords,
    value: l.value_loss_per_100,
    lineStyle: {
      width: l.width,
      color: l.vsi < 93 ? C.red : l.vsi < 95 ? C.amber : C.cyan,
      opacity: 0.75,
      curveness: 0.25,
    },
  }));

  return {
    backgroundColor: "transparent",
    geo: {
      map: "world",
      roam: true,
      zoom: 1.15,
      center: [-30, 20],
      itemStyle: {
        areaColor: "#0a0e14",
        borderColor: C.border,
        borderWidth: 0.6,
      },
      emphasis: { itemStyle: { areaColor: "#111827" } },
      silent: true,
    },
    tooltip: {
      trigger: "item",
      formatter: (p: { data?: { coords?: unknown; value?: number }; name?: string }) => {
        const idx = data.indexOf(p.data as typeof data[0]);
        if (idx >= 0) return `${lines[idx].corridor}<br/>VSI ${lines[idx].vsi.toFixed(1)} · Loss $${lines[idx].value_loss_per_100.toFixed(2)}/100`;
        return "";
      },
    },
    series: [{
      type: "lines",
      coordinateSystem: "geo",
      zlevel: 2,
      effect: {
        show: true,
        period: 4,
        trailLength: 0.35,
        symbol: "circle",
        symbolSize: 4,
        color: C.gold,
      },
      lineStyle: { width: 1, opacity: 0.6, curveness: 0.25 },
      data,
    }, {
      type: "effectScatter",
      coordinateSystem: "geo",
      zlevel: 3,
      rippleEffect: { brushType: "stroke", scale: 3, period: 5 },
      symbolSize: 8,
      itemStyle: { color: C.cyan, shadowBlur: 12, shadowColor: C.cyan },
      data: lines.flatMap((l) => [
        { name: l.sender, value: [...l.coords[0], l.vsi] },
        { name: l.receiver, value: [...l.coords[1], l.vsi] },
      ]),
    }],
  };
}

export function lineageGraphOption(graph: LineageGraph) {
  const categories = [
    { name: "source", itemStyle: { color: C.gold } },
    { name: "layer", itemStyle: { color: C.purple } },
    { name: "module", itemStyle: { color: C.cyan } },
    { name: "ui", itemStyle: { color: C.green } },
  ];
  const catMap: Record<string, number> = { source: 0, layer: 1, module: 2, ui: 3 };
  return {
    backgroundColor: "transparent",
    tooltip: {},
    legend: [{ data: categories.map((c) => c.name), textStyle: { color: C.muted }, bottom: 0 }],
    series: [{
      type: "graph",
      layout: "force",
      roam: true,
      draggable: true,
      force: { repulsion: 280, edgeLength: [80, 140], gravity: 0.08 },
      label: { show: true, color: C.text, fontSize: 9, fontFamily: "Inter" },
      lineStyle: { color: "source", curveness: 0.15, opacity: 0.55 },
      emphasis: { focus: "adjacency", lineStyle: { width: 3 } },
      categories,
      data: graph.nodes.map((n) => ({
        id: n.id,
        name: n.name,
        category: catMap[n.category] ?? 2,
        symbolSize: n.category === "ui" ? 42 : n.category === "source" ? 36 : 32,
      })),
      edges: graph.links.map((l) => ({ source: l.source, target: l.target })),
    }],
  };
}

export function settlementTimelineOption(stages: TimelineStage[], frame: number) {
  const visible = stages.slice(0, Math.max(1, frame));
  return {
    backgroundColor: "transparent",
    grid: baseGrid,
    xAxis: {
      type: "category",
      data: visible.map((s) => s.stage),
      axisLabel: { color: C.muted, fontSize: 10, rotate: 20 },
      axisLine: { lineStyle: { color: C.border } },
    },
    yAxis: [
      {
        type: "value",
        name: "Hours",
        nameTextStyle: { color: C.muted },
        axisLabel: { color: C.muted },
        splitLine: { lineStyle: { color: C.border, type: "dashed" } },
      },
      {
        type: "value",
        name: "Score",
        max: 100,
        axisLabel: { color: C.muted },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "Cumulative hours",
        type: "bar",
        data: visible.map((s) => s.hours),
        itemStyle: {
          color: {
            type: "linear", x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: C.cyan }, { offset: 1, color: "#0e7490" }],
          },
          borderRadius: [4, 4, 0, 0],
        },
        animationDuration: 600,
        animationEasing: "cubicOut",
      },
      {
        name: "Finality score",
        type: "line",
        yAxisIndex: 1,
        data: visible.map((s) => s.score),
        smooth: true,
        symbol: "circle",
        symbolSize: 8,
        lineStyle: { color: C.gold, width: 2 },
        itemStyle: { color: C.gold },
        animationDuration: 600,
      },
    ],
    tooltip: { trigger: "axis" },
  };
}

export function finalityMatrixOption(rows: { stablecoin: string; ledger: number; economic: number; sfqi: number }[]) {
  return {
    backgroundColor: "transparent",
    grid: baseGrid,
    xAxis: {
      name: "Ledger finality",
      min: 0, max: 100,
      nameTextStyle: { color: C.muted },
      axisLabel: { color: C.muted },
      splitLine: { lineStyle: { color: C.border } },
    },
    yAxis: {
      name: "Economic finality",
      min: 0, max: 100,
      nameTextStyle: { color: C.muted },
      axisLabel: { color: C.muted },
      splitLine: { lineStyle: { color: C.border } },
    },
    series: [{
      type: "scatter",
      symbolSize: (val: number[]) => Math.max(12, val[2] / 4),
      data: rows.map((r) => [r.ledger, r.economic, r.sfqi, r.stablecoin]),
      itemStyle: {
        color: (p: { data: number[] }) => {
          const gap = p.data[0] - p.data[1];
          return gap > 15 ? C.amber : C.cyan;
        },
        shadowBlur: 8,
        shadowColor: "rgba(56,189,248,0.35)",
      },
      emphasis: { scale: 1.3 },
    }],
    tooltip: {
      formatter: (p: { data: [number, number, number, string] }) =>
        `${p.data[3]}<br/>Ledger ${p.data[0].toFixed(1)} · Economic ${p.data[1].toFixed(1)}<br/>SFQI ${p.data[2].toFixed(1)}`,
    },
  };
}

export function vsiBarOption(corridors: string[], values: number[]) {
  return {
    backgroundColor: "transparent",
    grid: { ...baseGrid, bottom: 72 },
    xAxis: {
      type: "category",
      data: corridors,
      axisLabel: { color: C.muted, rotate: 35, fontSize: 9 },
      axisLine: { lineStyle: { color: C.border } },
    },
    yAxis: {
      type: "value",
      min: 88,
      axisLabel: { color: C.muted },
      splitLine: { lineStyle: { color: C.border } },
    },
    series: [{
      type: "bar",
      data: values.map((v) => ({
        value: v,
        itemStyle: {
          color: v < 93 ? C.red : v < 95 ? C.amber : C.cyan,
          borderRadius: [3, 3, 0, 0],
        },
      })),
    }],
    tooltip: { trigger: "axis" },
  };
}
