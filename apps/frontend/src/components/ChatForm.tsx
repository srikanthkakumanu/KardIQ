"use client";

import { useState, type FormEvent } from "react";

import styles from "./ChatForm.module.css";

interface ChatFormProps {
  onSubmit: (message: string) => void;
  disabled: boolean;
}

export function ChatForm({ onSubmit, disabled }: ChatFormProps) {
  const [message, setMessage] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || disabled) {
      return;
    }
    onSubmit(trimmed);
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <label htmlFor="question" className={styles.label}>
        Ask a question about your knowledge cards
      </label>
      <textarea
        id="question"
        className={styles.textarea}
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        placeholder="How does LangChain connect to OpenAI?"
        rows={3}
        disabled={disabled}
      />
      <button type="submit" className={styles.button} disabled={disabled || !message.trim()}>
        {disabled ? "Asking..." : "Ask"}
      </button>
    </form>
  );
}
