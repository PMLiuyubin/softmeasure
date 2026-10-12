export interface LineScore {
  id: string;
  name: string;
  pool: string;
  kind: string;
  R2: number;
  RMSE: number;
  n: number;
  default_on: boolean;
}

export interface SeriesRow {
  t: string;
  nir_arrival: number;
  line1: number;
  line2: number;
  line3: number;
  line4: number;
  line5: number;
  line6: number;
  line7: number;
}

export interface FoundationBody {
  dataset: {
    n_rows: number;
    time_min: string;
    time_max: string;
    acceptance: { start: string; end: string; rows_in_snapshot: number };
  };
  mechanism: { formula: string; weights: string; coefficients: Record<string, number> };
  predict: { live_infer: { enabled: boolean; armed: boolean; feature_columns: number; reason: string } };
  evaluate: { n: number; window: string; ruler: string; lines: LineScore[] };
  mining: { offline_only: boolean; imported_by_web: boolean; note: string; last: { pairs?: { with: string; r: number; n: number }[] } | null };
}
