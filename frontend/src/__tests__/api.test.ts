import { describe, expect, it, vi } from "vitest";
import { api } from "../lib/api";

describe("api helpers", () => {
  it("requests tournament data", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      if (String(input).endsWith("/api/health")) {
        return new Response(JSON.stringify({ status: "ok" }));
      }

      return new Response(
        JSON.stringify({
          slug: "world_cup_2026",
          groups: {},
          host_countries: [],
          host_cities: [],
          format: {},
          name: "",
          start_date: "",
          end_date: "",
        }),
      );
    });

    const result = await api.getTournamentCurrent();
    expect(result.slug).toBe("world_cup_2026");
    expect(fetchSpy).toHaveBeenCalled();
    fetchSpy.mockRestore();
  });
});
