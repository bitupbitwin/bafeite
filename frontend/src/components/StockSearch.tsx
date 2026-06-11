import { useEffect, useRef, useState } from 'react';
import { searchStocks } from '../api/stockApi';
import type { StockInfo } from '../types';

interface Props {
  selected: StockInfo | null;
  onSelect: (stock: StockInfo | null) => void;
}

export default function StockSearch({ selected, onSelect }: Props) {
  const [keyword, setKeyword] = useState('');
  const [results, setResults] = useState<StockInfo[]>([]);
  const [error, setError] = useState('');
  const timer = useRef<number>();

  useEffect(() => {
    window.clearTimeout(timer.current);
    if (!keyword.trim() || (selected && keyword === `${selected.name} ${selected.code}`)) {
      setResults([]);
      return;
    }
    timer.current = window.setTimeout(async () => {
      try {
        setError('');
        setResults(await searchStocks(keyword.trim()));
      } catch (e) {
        setError((e as Error).message);
        setResults([]);
      }
    }, 300);
    return () => window.clearTimeout(timer.current);
  }, [keyword, selected]);

  return (
    <div className="stock-search">
      <input
        className="search-input"
        placeholder="例如: 普冉股份 / 688766"
        value={keyword}
        onChange={(e) => {
          setKeyword(e.target.value);
          onSelect(null);
        }}
      />
      {error && <p className="error-text">{error}</p>}
      {results.length > 0 && (
        <ul className="search-results">
          {results.map((s) => (
            <li
              key={s.code}
              onClick={() => {
                onSelect(s);
                setKeyword(`${s.name} ${s.code}`);
                setResults([]);
              }}
            >
              <span className="stock-name">{s.name}</span>
              <span className="stock-code">
                {s.code} · {s.market}
                {s.exchange ? `/${s.exchange}` : ''}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
