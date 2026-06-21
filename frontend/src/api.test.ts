import { describe, it, expect, vi, afterEach } from "vitest";
import { runAssessment, fetchReport, ApiError } from "./api";
import type { AssessmentResponse } from "./types";

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const oneShot = () => [{ key: "frontal" as const, blob: new Blob(["x"]), filename: "frontal.jpg" }];

describe("runAssessment", () => {
  it("POSTs multipart with auth headers and returns parsed JSON", async () => {
    const payload = { aesthetic_score: 90, views_analyzed: ["frontal"] };
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(payload));
    vi.stubGlobal("fetch", fetchMock);

    const out = await runAssessment(oneShot());
    expect(out).toMatchObject(payload);

    expect(fetchMock).toHaveBeenCalledOnce();
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(String(url)).toMatch(/\/assessment$/);
    expect(init.method).toBe("POST");
    expect(init.body).toBeInstanceOf(FormData);
    const headers = init.headers as Record<string, string>;
    expect(headers.Authorization).toMatch(/^Bearer /);
    expect(headers.apikey).toBeTruthy();
    // The browser must set the multipart boundary — we must NOT send Content-Type.
    expect(headers["Content-Type"]).toBeUndefined();
  });

  it("throws ApiError(422) with the detail message when no face is detected", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ detail: "no face" }, 422)));
    const err = await runAssessment(oneShot()).catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err).toMatchObject({ status: 422, message: "no face" });
  });

  it("wraps a non-JSON error body", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("upstream boom", { status: 502 })));
    await expect(runAssessment(oneShot())).rejects.toMatchObject({ status: 502 });
  });
});

describe("fetchReport", () => {
  it("returns the PDF blob on success", async () => {
    const pdf = new Blob(["%PDF-1.4"], { type: "application/pdf" });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(pdf, { status: 200 })));
    const blob = await fetchReport({ aesthetic_score: 90 } as unknown as AssessmentResponse);
    expect(blob).toBeInstanceOf(Blob);
    expect(blob.size).toBeGreaterThan(0);
  });

  it("throws ApiError on a failed report", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("nope", { status: 500 })));
    await expect(fetchReport({} as AssessmentResponse)).rejects.toBeInstanceOf(ApiError);
  });
});
