export interface StockInfo {
  code: string;
  name: string;
  market: string;
  exchange: string;
}

export interface KLineBar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount?: number | null;
  pct_chg?: number | null;
  ma5?: number | null;
  ma10?: number | null;
  ma20?: number | null;
}

export interface KLineResponse {
  code: string;
  name: string;
  is_mock: boolean;
  data: KLineBar[];
}

export interface AnalyzeResult {
  stock: { code: string; name: string };
  period: string;
  is_mock: boolean;
  current_price: number;
  today_pct_chg: number;
  current_state: string;
  score: number;
  up_probability: number;
  down_probability: number;
  expected_up_range: string;
  expected_down_range: string;
  support_price: number;
  pressure_price: number;
  explanation: string[];
  risk_warning: string;
}
