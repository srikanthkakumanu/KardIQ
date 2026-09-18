import type { ChatResponse } from "@/src/types";

import styles from "./AnswerPanel.module.css";

interface AnswerPanelProps {
  result: ChatResponse;
}

export function AnswerPanel({ result }: AnswerPanelProps) {
  return (
    <section className={styles.panel} aria-live="polite">
      <p className={styles.answer}>{result.answer}</p>
      {result.sources.length > 0 && (
        <div className={styles.sources}>
          <h3 className={styles.sourcesTitle}>Sources</h3>
          <ul className={styles.sourcesList}>
            {result.sources.map((source) => (
              <li key={source.cardId}>{source.title}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
