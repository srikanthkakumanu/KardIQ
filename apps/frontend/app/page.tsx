"use client";

import { useEffect, useRef, useState } from "react";

import { AgentApiError, postChat } from "@/src/api/agentClient";
import { AnswerPanel } from "@/src/components/AnswerPanel";
import { ChatForm } from "@/src/components/ChatForm";
import { ErrorBanner } from "@/src/components/ErrorBanner";
import { LoadingIndicator } from "@/src/components/LoadingIndicator";
import { TraceInspector } from "@/src/components/TraceInspector";
import type { ChatError, ChatResponse } from "@/src/types";

import styles from "./page.module.css";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<ChatError | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  async function handleSubmit(message: string) {
    abortControllerRef.current?.abort();
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await postChat({ message }, controller.signal);
      setResult(response);
      if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        return;
      }
      if (err instanceof AgentApiError) {
        setError({ code: err.code, message: err.message });
      } else {
        setError({ code: "NETWORK_ERROR", message: "Could not reach the agent. Is it running?" });
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>Knowledge Card Assistant</h1>
      <p className={styles.subtitle}>
        Ask a question grounded in your knowledge cards and their graph relationships.
      </p>
      <ChatForm onSubmit={handleSubmit} disabled={loading} />
      {loading && <LoadingIndicator />}
      {error && <ErrorBanner code={error.code} message={error.message} />}
      {result && !loading && (
        <>
          {result.answer && <AnswerPanel result={result} />}
          <TraceInspector result={result} />
        </>
      )}
    </main>
  );
}
