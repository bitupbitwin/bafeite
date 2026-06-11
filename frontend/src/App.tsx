import { useState } from 'react';
import HomePage from './pages/HomePage';
import ResultPage from './pages/ResultPage';
import type { StockInfo } from './types';

const RISK_WARNING =
  '本工具仅基于历史价格、成交量和技术指标进行统计分析，不构成任何投资建议。' +
  '股票价格受政策、业绩、市场情绪、资金流、突发消息等多种因素影响，模型预测结果可能失效。' +
  '用户应独立判断并自行承担投资风险。';

export default function App() {
  const [selected, setSelected] = useState<{ stock: StockInfo; periodDays: number } | null>(null);

  return (
    <div className="app">
      <header className="app-header">
        <h1 onClick={() => setSelected(null)}>📈 股票台阶式上涨预测工具</h1>
        <p className="subtitle">基于「上涨—回调—横盘—再上涨」台阶规律的次日涨跌概率估算</p>
      </header>

      <main>
        {selected ? (
          <ResultPage
            stock={selected.stock}
            periodDays={selected.periodDays}
            onBack={() => setSelected(null)}
          />
        ) : (
          <HomePage onAnalyze={(stock, periodDays) => setSelected({ stock, periodDays })} />
        )}
      </main>

      <footer className="risk-footer">{RISK_WARNING}</footer>
    </div>
  );
}
