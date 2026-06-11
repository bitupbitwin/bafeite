import { useEffect, useState } from 'react';
import { analyzeStock, getKLine } from '../api/stockApi';
import PredictionCard from '../components/PredictionCard';
import KLineChart from '../components/KLineChart';
import ExplanationPanel from '../components/ExplanationPanel';
import type { AnalyzeResult, KLineResponse, StockInfo } from '../types';

interface Props {
  stock: StockInfo;
  periodDays: number;
  onBack: () => void;
}

export default function ResultPage({ stock, periodDays, onBack }: Props) {
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [kline, setKline] = useState<KLineResponse | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError('');
    Promise.all([analyzeStock(stock.code, periodDays), getKLine(stock.code, periodDays)])
      .then(([analysis, bars]) => {
        if (cancelled) return;
        setResult(analysis);
        setKline(bars);
      })
      .catch((e) => !cancelled && setError((e as Error).message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [stock.code, periodDays]);

  return (
    <div className="result-page">
      <button className="back-btn" onClick={onBack}>
        ← 返回重新选择
      </button>

      {loading && <p className="loading">正在获取数据并分析…</p>}
      {error && <p className="error-text">{error}</p>}

      {result && (
        <>
          {result.is_mock && (
            <div className="mock-banner">⚠️ 当前展示的是演示数据(后端未连接真实行情源)</div>
          )}
          <PredictionCard result={result} />
          {kline && <KLineChart bars={kline.data} />}
          <ExplanationPanel explanation={result.explanation} riskWarning={result.risk_warning} />
        </>
      )}
    </div>
  );
}
