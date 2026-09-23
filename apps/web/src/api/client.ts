export type Candidate = { id: string; confidence?: string | number; reason?: string };
export type RoutingTrace = {
  turn_id?: string; trace_id?: string; language?: string; selected?: Candidate[];
  alternatives?: Candidate[]; slots?: Record<string, unknown>; extracted_slots?: Record<string, unknown>;
  clarification?: { required?: boolean; question?: string };
  fallback?: { active?: boolean; reason?: string }; handoff?: unknown;
  execution?: { mode?: string; status?: string; preview_id?: string; action?: string; slot?: string };
  latency_ms?: Record<string, number>; metadata?: Record<string, unknown>;
};
export type Turn = { conversation_id: string; turn_id: string; trace_id: string; assistant_message: string; routing: RoutingTrace; execution: NonNullable<RoutingTrace["execution"]> };
const base = (import.meta.env.VITE_API_URL || "/api").replace(/\/$/, "");
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try { response = await fetch(`${base}${path}`, { ...init, signal: AbortSignal.timeout(45000) }); }
  catch { throw new Error("We couldn’t connect to the server. Check that the backend is running, then try again."); }
  if (!response.ok) {
    if (response.status === 409) throw new Error("This conversation has reached its limit. Start a new session to continue.");
    if (response.status === 404) throw new Error("This session is no longer available. Start a new session to continue.");
    throw new Error("The request couldn’t be completed. Check the backend connection and try again.");
  }
  return response.json();
}
export function checkHealth() { return request<{ status: string; catalog_version: string }>("/health"); }
export function createConversation() { return request<{ conversation_id: string }>("/v1/conversations", { method: "POST" }); }
export function sendText(id: string, text: string, confirmation?: { preview_id: string; confirmed: boolean }) {
  return request<Turn>(`/v1/conversations/${id}/turns`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, input_mode: "text", client_turn_id: crypto.randomUUID(), ...confirmation }) });
}
export function getTrace(conversation: string, turn: string) { return request<RoutingTrace>(`/v1/conversations/${conversation}/traces/${turn}`); }
