import { describe, expect, it } from "vitest";
import { totalLatency } from "./trace";
describe("backend timing display", () => {
  it("uses the backend total without double-counting stages", () => {
    expect(totalLatency({ routing: { duration_ms: 80, status: "measured" }, total: { duration_ms: 100, status: "measured" } })).toBe(100);
  });
  it("handles failed stages and legacy example data", () => {
    expect(totalLatency({ routing: { duration_ms: null, status: "failed" } })).toBeUndefined();
    expect(totalLatency({ triage: 12, routing: 684 })).toBe(696);
    expect(totalLatency({ total: { duration_ms: 0, status: "measured" } })).toBe(0);
  });
});
