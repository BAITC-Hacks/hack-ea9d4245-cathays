export type Candidate = { id: string; confidence?: string | number; reason?: string };
export type StageTiming = { duration_ms: number | null; status: string };
export type RoutingTrace = {
  turn_id?: string; trace_id?: string; language?: string; selected?: Candidate[];
  alternatives?: Candidate[]; slots?: Record<string, unknown>; extracted_slots?: Record<string, unknown>;
  clarification?: { required?: boolean; question?: string };
  fallback?: { active?: boolean; reason?: string }; handoff?: unknown;
  execution?: { mode?: string; status?: string; preview_id?: string; action?: string; slot?: string };
  latency_ms?: Record<string, number | StageTiming>; metadata?: Record<string, unknown>;
};
export type Turn = { conversation_id: string; turn_id: string; trace_id: string; assistant_message: string; routing: RoutingTrace; execution: NonNullable<RoutingTrace["execution"]> };
const base = (import.meta.env.VITE_API_URL || "/api").replace(/\/$/, "");
export class ApiError extends Error {
  constructor(message: string, public status: number, public code?: string) { super(message); }
}
async function request<T>(path: string, init?: RequestInit, timeout = 45000): Promise<T> {
  let response: Response;
  try { response = await fetch(`${base}${path}`, { ...init, signal: AbortSignal.timeout(timeout) }); }
  catch { throw new Error("We couldn’t connect to the server. Check that the backend is running, then try again."); }
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const code = typeof payload.code === "string" ? payload.code : undefined;
    const message = code === "conversation_limit" ? "This conversation has reached its limit. Start a new session to continue."
      : code === "preview_not_found" ? "This action preview is no longer available. Send a new message to prepare it again."
      : response.status === 404 ? "This session is no longer available. Start a new session to continue."
      : response.status === 422 ? "Please check your message and action details, then try again."
      : "The request couldn’t be completed. Check the backend connection and try again.";
    throw new ApiError(message, response.status, code);
  }
  try { return await response.json(); }
  catch { throw new Error("The server returned an invalid response. Check the API URL and try again."); }
}
export function checkHealth() { return request<{ status: string; catalog_version: string; provider_configured?: boolean }>("/health", undefined, 5000); }
export function createConversation() { return request<{ conversation_id: string }>("/v1/conversations", { method: "POST" }); }
export function sendText(id: string, text: string, confirmation?: { preview_id: string; confirmed: boolean }, clientTurnId: string = crypto.randomUUID()) {
  return request<Turn>(`/v1/conversations/${id}/turns`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, input_mode: "text", client_turn_id: clientTurnId, ...confirmation }) });
}
export function getTrace(conversation: string, turn: string) { return request<RoutingTrace>(`/v1/conversations/${conversation}/traces/${turn}`); }
