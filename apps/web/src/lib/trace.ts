import type { RoutingTrace } from "@/api/client";

export function totalLatency(timings: RoutingTrace["latency_ms"]): number | undefined {
  const duration = (entry: NonNullable<typeof timings>[string] | undefined) => {
    const value = typeof entry === "number" ? entry : entry?.duration_ms;
    return typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : undefined;
  };
  const total = duration(timings?.total);
  if (total !== undefined) return total;
  const measured = Object.entries(timings ?? {}).filter(([key]) => key !== "total").map(([, value]) => duration(value)).filter((value): value is number => value !== undefined);
  return measured.length ? measured.reduce((sum, value) => sum + value, 0) : undefined;
}
