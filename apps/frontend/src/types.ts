export interface ChatRequest {
  message: string;
  sessionId?: string;
}

export interface ToolCallTrace {
  tool: string;
  success: boolean;
  latencyMs: number | null;
}

export interface Source {
  cardId: string;
  title: string;
}

export interface ChatError {
  code: string;
  message: string;
}

export interface ChatResponse {
  answer: string;
  provider: string;
  model: string;
  toolCalls: ToolCallTrace[];
  sources: Source[];
  contextSnippets: string[];
  requestId: string;
  error: ChatError | null;
}

export interface ApiErrorBody {
  code: string;
  message: string;
  requestId: string;
}
