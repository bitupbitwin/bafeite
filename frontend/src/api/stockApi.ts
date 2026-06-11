import type { AnalyzeResult, KLineResponse, StockInfo } from '../types';

const BASE = import.meta.env.VITE_API_BASE ?? '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) {
    let detail = `请求失败 (${res.status})`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export function searchStocks(keyword: string): Promise<StockInfo[]> {
  return request(`/stocks/search?keyword=${encodeURIComponent(keyword)}`);
}

export function getKLine(code: string, period: number): Promise<KLineResponse> {
  return request(`/stocks/${code}/kline?period=${period}`);
}

export function analyzeStock(code: string, periodDays: number): Promise<AnalyzeResult> {
  return request('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, period_days: periodDays }),
  });
}
