import { useState } from 'react';
import StockSearch from '../components/StockSearch';
import type { StockInfo } from '../types';

const PERIODS = [
  { label: '最近7个交易日', days: 7 },
  { label: '最近15个交易日', days: 15 },
  { label: '最近1个月', days: 22 },
  { label: '最近2个月', days: 44 },
  { label: '最近3个月', days: 66 },
];

interface Props {
  onAnalyze: (stock: StockInfo, periodDays: number) => void;
}

export default function HomePage({ onAnalyze }: Props) {
  const [stock, setStock] = useState<StockInfo | null>(null);
  const [periodDays, setPeriodDays] = useState(22);

  return (
    <div className="home-page">
      <section className="card">
        <label className="field-label">输入股票名称或代码</label>
        <StockSearch selected={stock} onSelect={setStock} />

        <label className="field-label">分析周期</label>
        <div className="period-selector">
          {PERIODS.map((p) => (
            <button
              key={p.days}
              className={`period-btn ${periodDays === p.days ? 'active' : ''}`}
              onClick={() => setPeriodDays(p.days)}
            >
              {p.label}
            </button>
          ))}
        </div>

        <button
          className="analyze-btn"
          disabled={!stock}
          onClick={() => stock && onAnalyze(stock, periodDays)}
        >
          开始分析
        </button>
        {periodDays < 20 && (
          <p className="hint">提示: 模型至少需要 20 个交易日数据, 周期过短时只做简单趋势判断。</p>
        )}
      </section>
    </div>
  );
}
