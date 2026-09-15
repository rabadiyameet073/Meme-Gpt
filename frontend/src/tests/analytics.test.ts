import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  trackEvent,
  trackMemeSearch,
  trackMemeDownload,
  trackMemeShare,
  trackMemeFavorite,
} from "../lib/analytics";

describe("Analytics & Telemetry (Guide 13 - Umami)", () => {
  const originalUmami = (window as any).umami;

  beforeEach(() => {
    vi.clearAllMocks();
    (window as any).umami = {
      track: vi.fn(),
    };
  });

  afterEach(() => {
    (window as any).umami = originalUmami;
  });

  it("dispatches custom events to window.umami.track when available", () => {
    trackEvent("custom_action", { foo: "bar" });
    expect((window as any).umami.track).toHaveBeenCalledWith("custom_action", { foo: "bar" });
  });

  it("gracefully handles missing window.umami without throwing errors", () => {
    delete (window as any).umami;
    expect(() => {
      trackEvent("test_event", { query: "hello" });
    }).not.toThrow();
  });

  it("gracefully catches exceptions inside window.umami.track", () => {
    (window as any).umami = {
      track: vi.fn().mockImplementation(() => {
        throw new Error("Network offline");
      }),
    };
    expect(() => {
      trackEvent("failing_event");
    }).not.toThrow();
  });

  it("tracks search queries via trackMemeSearch", () => {
    trackMemeSearch("boss monday", { format: "gif" });
    expect((window as any).umami.track).toHaveBeenCalledWith("meme_search", {
      query: "boss monday",
      format: "gif",
    });
  });

  it("tracks download actions via trackMemeDownload", () => {
    trackMemeDownload("drake-pointing", "mp4");
    expect((window as any).umami.track).toHaveBeenCalledWith("meme_download", {
      meme_slug: "drake-pointing",
      format: "mp4",
    });
  });

  it("tracks share actions via trackMemeShare", () => {
    trackMemeShare("distracted-boyfriend", "whatsapp");
    expect((window as any).umami.track).toHaveBeenCalledWith("meme_share", {
      meme_slug: "distracted-boyfriend",
      channel: "whatsapp",
    });
  });

  it("tracks favorites toggle via trackMemeFavorite", () => {
    trackMemeFavorite("meme_123", true);
    expect((window as any).umami.track).toHaveBeenCalledWith("meme_favorite", {
      meme_id: "meme_123",
      is_favorite: true,
    });
  });
});
