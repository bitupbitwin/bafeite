interface Props {
  explanation: string[];
  riskWarning: string;
}

export default function ExplanationPanel({ explanation, riskWarning }: Props) {
  return (
    <section className="card explanation-panel">
      <h3>模型解释</h3>
      <ul>
        {explanation.map((line, i) => (
          <li key={i}>{line}</li>
        ))}
      </ul>
      <p className="risk-note">{riskWarning}</p>
    </section>
  );
}
