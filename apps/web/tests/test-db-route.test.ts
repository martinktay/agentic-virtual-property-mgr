import { afterEach, describe, expect, it, vi } from "vitest";

const queryMock = vi.fn();
const endMock = vi.fn();

vi.mock("pg", () => ({
  Client: vi.fn(() => ({
    connect: vi.fn(),
    query: queryMock,
    end: endMock
  }))
}));

describe("test-db route", () => {
  afterEach(() => {
    vi.resetModules();
    vi.unstubAllEnvs();
    queryMock.mockReset();
    endMock.mockReset();
  });

  it("returns 503 when DATABASE_URL is missing", async () => {
    vi.stubEnv("DATABASE_URL", "");
    const { GET } = await import("../app/api/test-db/route");

    const response = await GET();
    const body = await response.json();

    expect(response.status).toBe(503);
    expect(body).toEqual({
      ok: false,
      service: "aurora-dsql",
      error: "DATABASE_URL is not configured"
    });
  });

  it("runs SELECT NOW against the configured database", async () => {
    vi.stubEnv("DATABASE_URL", "postgresql://admin:token@example.dsql.us-east-1.on.aws:5432/postgres?sslmode=require");
    queryMock.mockResolvedValueOnce({ rows: [{ now: "2026-06-12T12:00:00.000Z" }] });
    const { GET } = await import("../app/api/test-db/route");

    const response = await GET();
    const body = await response.json();

    expect(response.status).toBe(200);
    expect(queryMock).toHaveBeenCalledWith("SELECT NOW() AS now");
    expect(endMock).toHaveBeenCalledOnce();
    expect(body).toEqual({
      ok: true,
      service: "aurora-dsql",
      timestamp: "2026-06-12T12:00:00.000Z"
    });
  });
});
