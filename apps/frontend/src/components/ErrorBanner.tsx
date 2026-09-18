import styles from "./ErrorBanner.module.css";

interface ErrorBannerProps {
  code: string;
  message: string;
}

export function ErrorBanner({ code, message }: ErrorBannerProps) {
  return (
    <div className={styles.banner} role="alert">
      <strong className={styles.code}>{code}</strong>
      <span>{message}</span>
    </div>
  );
}
