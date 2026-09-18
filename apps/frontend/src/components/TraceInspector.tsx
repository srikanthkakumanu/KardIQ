import type { ChatResponse } from "@/src/types";

import styles from "./TraceInspector.module.css";

interface TraceInspectorProps {
  result: ChatResponse;
}

// The "compact inspectable panel" required by apps/CLAUDE.md's UX
// standards, so a user can see exactly which tools ran, which provider
// answered, and the request id to correlate with backend logs.
export function TraceInspector({ result }: TraceInspectorProps) {
  return (
    <details className={styles.details}>
      <summary className={styles.summary}>How this answer was produced</summary>
      <dl className={styles.grid}>
        <dt>Provider</dt>
        <dd>{result.provider}</dd>
        <dt>Model</dt>
        <dd>{result.model}</dd>
        <dt>Request ID</dt>
        <dd className={styles.mono}>{result.requestId}</dd>
      </dl>
      <ul className={styles.toolCalls}>
        {result.toolCalls.map((call, index) => (
          <li key={`${call.tool}-${index}`} className={call.success ? styles.success : styles.failure}>
            {call.tool} - {call.success ? "ok" : "failed"}
            {call.latencyMs !== null ? ` (${call.latencyMs.toFixed(1)}ms)` : null}
          </li>
        ))}
      </ul>
      {result.contextSnippets.length > 0 && (
        <div>
          <h4 className={styles.contextTitle}>Context used</h4>
          <ul className={styles.context}>
            {result.contextSnippets.map((snippet, index) => (
              <li key={index}>{snippet}</li>
            ))}
          </ul>
        </div>
      )}
    </details>
  );
}
