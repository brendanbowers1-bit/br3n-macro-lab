export type DashboardPayload = {
  meta: { generated_at: string; lab: string; disclaimer: string };
  modules: Record<string, boolean>;
  executive: {
    global_vsi?: number;
    worst_corridor?: string;
    worst_vsi?: number;
    avg_loss_per_100?: number;
    official_coverage_pct?: number;
    worst_settlement_entity?: string;
    worst_sdi?: number;
    worst_stablecoin?: string;
    worst_sfqi?: number;
  };
  vsi: {
    corridor_summary: CorridorRow[];
    outputs_sample: Record<string, unknown>[];
    sensitivity_sample: Record<string, unknown>[];
  };
  settlement: Record<string, Record<string, unknown>[]>;
  stablecoin: Record<string, Record<string, unknown>[]>;
  data_lake: Record<string, unknown>;
  audit: Record<string, unknown>;
  coverage: Record<string, Record<string, number | null>>;
  hypotheses: {
    vsi: Record<string, unknown>[];
    settlement: Record<string, unknown>[];
    stablecoin: Record<string, unknown>[];
    flagship_questions: string[];
  };
  gallery: { title: string; path: string; module: string; ext: string }[];
  visualizations: {
    sankey_by_corridor: SankeyPayload[];
    value_flow_lines: ValueFlowLine[];
    lineage_graph: LineageGraph;
    settlement_timeline: TimelineStage[];
    finality_matrix: FinalityRow[];
    risk_relocation_sankey: SankeyPayload;
  };
};

export type CorridorRow = {
  corridor: string;
  value_survival_index: number;
  value_loss_usd_per_100?: number;
  data_quality_score?: number;
  data_quality_grade?: string;
  mock_data_flag?: boolean;
};

export type SankeyPayload = {
  corridor?: string;
  nodes: { name: string }[];
  links: { source: number; target: number; value: number }[];
  methodology?: string;
  note?: string;
};

export type ValueFlowLine = {
  corridor: string;
  sender: string;
  receiver: string;
  coords: [number, number][];
  value_loss_per_100: number;
  vsi: number;
  width: number;
};

export type LineageGraph = {
  nodes: { id: string; name: string; category: string; tier?: number }[];
  links: { source: string; target: string }[];
};

export type TimelineStage = {
  stage: string;
  hours: number;
  score: number;
};

export type FinalityRow = {
  stablecoin: string;
  ledger_finality_score: number;
  economic_finality_score: number;
  stablecoin_finality_quality_index: number;
  mock_data_flag?: boolean;
};
