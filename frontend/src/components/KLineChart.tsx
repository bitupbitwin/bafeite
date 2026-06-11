import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { KLineBar } from '../types';

const UP_COLOR = '#e53935';
const DOWN_COLOR = '#26a69a';

export default function KLineChart({ bars }: { bars: KLineBar[] }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current || bars.length === 0) return;
    const chart = echarts.init(ref.current);

    const dates = bars.map((b) => b.date);
    const candles = bars.map((b) => [b.open, b.close, b.low, b.high]);
    const volumes = bars.map((b, i) => ({
      value: b.volume,
      itemStyle: { color: b.close >= b.open ? UP_COLOR : DOWN_COLOR, opacity: 0.7 },
      dataIndex: i,
    }));
    const maLine = (key: 'ma5' | 'ma10' | 'ma20') =>
      bars.map((b) => (b[key] == null ? '-' : Number(b[key]!.toFixed(2))));

    chart.setOption({
      animation: false,
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
      legend: { data: ['K线', 'MA5', 'MA10', 'MA20'], top: 0 },
      grid: [
        { left: 50, right: 16, top: 30, height: '55%' },
        { left: 50, right: 16, top: '72%', height: '18%' },
      ],
      xAxis: [
        { type: 'category', data: dates, gridIndex: 0, boundaryGap: true },
        {
          type: 'category',
          data: dates,
          gridIndex: 1,
          boundaryGap: true,
          axisLabel: { show: false },
        },
      ],
      yAxis: [
        { scale: true, gridIndex: 0, splitLine: { lineStyle: { opacity: 0.3 } } },
        { scale: true, gridIndex: 1, axisLabel: { show: false }, splitLine: { show: false } },
      ],
      dataZoom: [
        { type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100 },
        { type: 'slider', xAxisIndex: [0, 1], bottom: 0, height: 18 },
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: candles,
          itemStyle: {
            color: UP_COLOR,
            color0: DOWN_COLOR,
            borderColor: UP_COLOR,
            borderColor0: DOWN_COLOR,
          },
        },
        { name: 'MA5', type: 'line', data: maLine('ma5'), smooth: true, showSymbol: false, lineStyle: { width: 1 } },
        { name: 'MA10', type: 'line', data: maLine('ma10'), smooth: true, showSymbol: false, lineStyle: { width: 1 } },
        { name: 'MA20', type: 'line', data: maLine('ma20'), smooth: true, showSymbol: false, lineStyle: { width: 1 } },
        { name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: volumes },
      ],
    });

    const onResize = () => chart.resize();
    window.addEventListener('resize', onResize);
    return () => {
      window.removeEventListener('resize', onResize);
      chart.dispose();
    };
  }, [bars]);

  return (
    <section className="card chart-card">
      <h3>K线与成交量</h3>
      <div ref={ref} className="kline-chart" />
    </section>
  );
}
