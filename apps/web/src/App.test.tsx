// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import App from "./App";
import { checkHealth, createConversation, getTrace, sendText } from "./api/client";

vi.mock("./api/client", () => ({ checkHealth: vi.fn(), createConversation: vi.fn(), getTrace: vi.fn(), sendText: vi.fn() }));
beforeEach(() => {
  vi.clearAllMocks();
  Element.prototype.scrollIntoView = vi.fn();
  vi.mocked(checkHealth).mockResolvedValue({ status: "ok", catalog_version: "test" });
  vi.mocked(createConversation).mockResolvedValue({ conversation_id: "conversation-1" });
});
afterEach(cleanup);
describe("routing studio", () => {
  it("populates a sample prompt without submitting it", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Explore coverage/ }));
    expect(screen.getByRole("textbox", { name: "Customer message" })).toHaveValue("Какие виды страхования у вас есть?");
    expect(sendText).not.toHaveBeenCalled();
    await screen.findByText("Backend connected");
  });
  it("shows an explicitly labeled example without backend requests", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Just looking around/ }));
    expect(screen.getByText("Illustrative example · no API request")).toBeInTheDocument();
    expect(screen.getByText("Coverage inquiry")).toBeInTheDocument();
    expect(createConversation).not.toHaveBeenCalled();
    expect(sendText).not.toHaveBeenCalled();
    fireEvent.click(screen.getAllByRole("button", { name: "New session" })[0]);
    expect(screen.getByText("Good conversations start here.")).toBeInTheDocument();
    await screen.findByText("Backend connected");
  });
  it("keeps a successful response when the separate trace request fails", async () => {
    vi.mocked(sendText).mockResolvedValue({ conversation_id: "conversation-1", turn_id: "1", trace_id: "trace-1", assistant_message: "How can I help with your policy?", routing: { language: "ru", selected: [{ id: "SC_TEST", confidence: "high" }] }, execution: { mode: "information", status: "complete" } });
    vi.mocked(getTrace).mockRejectedValue(new Error("trace unavailable"));
    render(<App />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "My insurance question" } });
    fireEvent.click(screen.getByRole("button", { name: "Send message" }));
    expect(await screen.findByText("How can I help with your policy?")).toBeInTheDocument();
    expect(screen.getByText("SC_TEST")).toBeInTheDocument();
    expect(sendText).toHaveBeenCalledWith("conversation-1", "My insurance question", undefined);
    expect(screen.getByRole("textbox")).toHaveValue("");
  });
  it("preserves the typed message and allows retry after a failed request", async () => {
    vi.mocked(sendText).mockRejectedValue(new Error("Backend unavailable"));
    render(<App />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Please help" } });
    fireEvent.click(screen.getByRole("button", { name: "Send message" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Backend unavailable");
    expect(screen.getByRole("textbox")).toHaveValue("Please help");
    await waitFor(() => expect(screen.getByRole("button", { name: "Send message" })).toBeEnabled());
  });
  it("restores a prior session from history", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Just looking around/ }));
    fireEvent.click(screen.getAllByRole("button", { name: "New session" })[0]);
    fireEvent.click(screen.getByRole("button", { name: /Session history/ }));
    fireEvent.click(screen.getByRole("button", { name: /Exploring insurance coverage 1 turns/ }));
    expect(screen.getByText("Illustrative example · no API request")).toBeInTheDocument();
    await screen.findByText("Backend connected");
  });
});
