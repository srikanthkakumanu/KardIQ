import styles from "./LoadingIndicator.module.css";

export function LoadingIndicator() {
  return (
    <div className={styles.loading} role="status" aria-live="polite">
      Thinking...
    </div>
  );
}
