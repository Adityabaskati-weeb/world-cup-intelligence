import { describe, expect, it, vi } from "vitest";

async function importApiModule() {
  vi.resetModules();
  return import("../lib/api");
}

describe("api helpers", () => {
  it("requests tournament data from the backend API", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          slug: "world_cup_2026",
          groups: {},
          host_countries: [],
          host_cities: [],
          format: { group_count: 12, teams_per_group: 4 },
          name: "FIFA World Cup 2026",
          start_date: "2026-06-11",
          end_date: "2026-07-19",
        }),
      ),
    );

    const { api } = await importApiModule();
    const result = await api.getTournamentCurrent();

    expect(result.slug).toBe("world_cup_2026");
    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringContaining("/api/tournament/current"),
      expect.objectContaining({
        headers: expect.objectContaining({ "Content-Type": "application/json" }),
      }),
    );
    fetchSpy.mockRestore();
  });

  it("surfaces backend validation errors instead of masking them with local fallbacks", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "home_team and away_team must be different." }), { status: 422 }),
    );

    const { api } = await importApiModule();
    await expect(
      api.predictMatch({
        home_team: "Mexico",
        away_team: "Mexico",
        neutral_site: false,
        stage: "group",
      }),
    ).rejects.toThrow("home_team and away_team must be different.");

    fetchSpy.mockRestore();
  });

  it("turns network failures into a clear backend connectivity message", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));

    const { api, describeError } = await importApiModule();
    await expect(api.getTournamentCurrent()).rejects.toThrow("Could not reach the Matchflow API.");

    try {
      await api.getTournamentCurrent();
    } catch (error) {
      expect(describeError(error)).toContain("Could not reach the Matchflow API.");
    }

    fetchSpy.mockRestore();
  });
});
