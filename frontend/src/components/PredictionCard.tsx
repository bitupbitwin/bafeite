import type { AnalyzeResult } from '../types';

const STATE_COLORS: Record<string, string> = {
  上涨阶段: '#e53935',
  突破阶段: '#d81b60',
  健康回调: '#fb8c00',
  横盘整理: '#757575',
  风险阶段: '#2e7d32',
  震荡观察: '#546e7a',
};

export default function PredictionCard({ result }: { result: AnalyzeResult }) {
  const pctClass = result.today_pct_chg >= 0 ? 'up' : 'down';
  return (
    <section className="card prediction-card">
      <div className="stock-title">
        <h2>
          {result.stock.name || '股票'} <span className="stock-code">{result.stock.code}</span>
        </h2>
        <span className="period-tag">{result.period}</span>
      </div>

      <div className="price-row">
        <span className="current-price">{result.current_price.toFixed(2)}</span>
        <span className={`pct-chg ${pctClass}`}>
          {result.today_pct_chg >= 0 ? '+' : ''}
          {result.today_pct_chg.toFixed(2)}%
        </span>
        <span
          className="state-badge"
          style={{ background: STATE_COLORS[result.current_state] ?? '#546e7a' }}
        >
          {result.current_state}
        </span>
      </div>

      {/* 用 flex-grow 按比例分配, 配合 min-width 保证极端概率下文字仍可见且不溢出容器 */}
      <div className="prob-bar">
        <div className="prob-up" style={{ flexGrow: result.up_probability }}>
          涨 {result.up_probability}%
        </div>
        <div className="prob-down" style={{ flexGrow: result.down_probability }}>
          跌 {result.down_probability}%
        </div>
      </div>

      <div className="metric-grid">
        <div className="metric">
          <label>预计上涨幅度</label>
          <strong className="up">{result.expected_up_range}</strong>
        </div>
        <div className="metric">
          <label>预计下跌幅度</label>
          <strong className="down">{result.expected_down_range}</strong>
        </div>
        <div className="metric">
          <label>支撑位</label>
          <strong>{result.support_price.toFixed(2)}</strong>
        </div>
        <div className="metric">
          <label>压力位</label>
          <strong>{result.pressure_price.toFixed(2)}</strong>
        </div>
        <div className="metric">
          <label>模型评分</label>
          <strong>{result.score} / ±100</strong>
        </div>
      </div>
    </section>
  );
}
