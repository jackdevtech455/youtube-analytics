"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type TrackerType = "channel" | "search";
type RankingMetric =
  | "views"
  | "likes"
  | "comments"
  | "views_delta"
  | "views_velocity"
  | "likes_delta"
  | "comments_delta";

type Tracker = {
  id: number;
  type: TrackerType;
  channel_id?: string | null;
  search_query?: string | null;
  top_n: number;
  candidate_pool_size: number;
  ranking_metric: RankingMetric;
  ranking_window_hours?: number | null;
  is_active: boolean;
  created_at: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function TrackersPage() {
  const [trackers, setTrackers] = useState<Tracker[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [trackerType, setTrackerType] = useState<TrackerType>("channel");
  const [channelId, setChannelId] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const [topN, setTopN] = useState<number>(20);
  const [poolSize, setPoolSize] = useState<number>(200);

  const [rankingMetric, setRankingMetric] = useState<RankingMetric>("views");
  const [windowHours, setWindowHours] = useState<number>(24);

  const rankingNeedsWindow = useMemo(
    () => rankingMetric.includes("delta") || rankingMetric.includes("velocity"),
    [rankingMetric]
  );

  async function fetchTrackers(): Promise<void> {
    setLoading(true);
    setErrorMessage(null);

    try {
      const response = await fetch(`${API_BASE}/trackers`);
      const data = await response.json();
      if (!response.ok) throw new Error(data?.detail || `HTTP ${response.status}`);
      setTrackers(data);
    } catch (error: any) {
      setErrorMessage(error?.message || "Failed to load trackers");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchTrackers();
  }, []);

  async function createTracker(): Promise<void> {
    setErrorMessage(null);

    const payload: any = {
      type: trackerType,
      top_n: topN,
      candidate_pool_size: poolSize,
      ranking_metric: rankingMetric,
      ranking_window_hours: rankingNeedsWindow ? windowHours : null,
    };

    if (trackerType === "channel") payload.channel_id = channelId.trim();
    if (trackerType === "search") payload.search_query = searchQuery.trim();

    try {
      const response = await fetch(`${API_BASE}/trackers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data?.detail || `HTTP ${response.status}`);

      setChannelId("");
      setSearchQuery("");
      await fetchTrackers();
    } catch (error: any) {
      setErrorMessage(error?.message || "Failed to create tracker");
    }
  }

  return (
    <div style={{ display: "grid", gap: 16, maxWidth: 980 }}>
      <h3 style={{ margin: 0 }}>Trackers</h3>

      <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
        <h4 style={{ marginTop: 0 }}>Create tracker</h4>

        <div style={{ display: "grid", gap: 10 }}>
          <label>
            Type:{" "}
            <select value={trackerType} onChange={(e) => setTrackerType(e.target.value as TrackerType)}>
              <option value="channel">Channel (hourly discovery)</option>
              <option value="search">Search (daily discovery)</option>
            </select>
          </label>

          {trackerType === "channel" ? (
            <label>
              Channel ID:{" "}
              <input
                value={channelId}
                onChange={(e) => setChannelId(e.target.value)}
                placeholder="UC... OR @handle OR https://youtube.com/@handle"
                style={{ width: "100%" }}
              />
            </label>
          ) : (
            <label>
              Search query:{" "}
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder='e.g. "van build timelapse"'
                style={{ width: "100%" }}
              />
            </label>
          )}

          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <label>
              Top N:{" "}
              <input type="number" min={1} max={200} value={topN} onChange={(e) => setTopN(parseInt(e.target.value || "20"))} />
            </label>
            <label>
              Pool size:{" "}
              <input type="number" min={20} max={1000} value={poolSize} onChange={(e) => setPoolSize(parseInt(e.target.value || "200"))} />
            </label>
          </div>

          <label>
            Ranking metric:{" "}
            <select value={rankingMetric} onChange={(e) => setRankingMetric(e.target.value as RankingMetric)}>
              <option value="views">Views (latest)</option>
              <option value="likes">Likes (latest)</option>
              <option value="comments">Comments (latest)</option>
              <option value="views_delta">Views delta (window)</option>
              <option value="views_velocity">Views/hour velocity (window)</option>
              <option value="likes_delta">Likes delta (window)</option>
              <option value="comments_delta">Comments delta (window)</option>
            </select>
          </label>

          {rankingNeedsWindow && (
            <label>
              Window hours:{" "}
              <input type="number" min={1} max={2160} value={windowHours} onChange={(e) => setWindowHours(parseInt(e.target.value || "24"))} />
              <span style={{ marginLeft: 8, color: "#666" }}>(24=1 day, 168=7 days)</span>
            </label>
          )}

          <button onClick={createTracker} style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd" }}>
            Create
          </button>

          {errorMessage && <div style={{ color: "crimson" }}>{errorMessage}</div>}
        </div>
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        {loading ? (
          <div>Loading…</div>
        ) : trackers.length === 0 ? (
          <div>No trackers yet.</div>
        ) : (
          trackers.map((tracker) => (
            <div key={tracker.id} style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                <div>
                  <div style={{ fontWeight: 700 }}>#{tracker.id} — {tracker.type.toUpperCase()}</div>
                  <div style={{ color: "#555", fontSize: 14 }}>
                    {tracker.type === "channel" ? `channel_id=${tracker.channel_id}` : `q=${tracker.search_query}`}
                  </div>
                  <div style={{ color: "#555", fontSize: 14 }}>
                    top_n={tracker.top_n}, pool={tracker.candidate_pool_size}, metric={tracker.ranking_metric}
                    {tracker.ranking_window_hours ? ` (${tracker.ranking_window_hours}h)` : ""}
                  </div>
                </div>
                <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                  <Link href={`/trackers/${tracker.id}`}>View →</Link>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div style={{ color: "#666", fontSize: 13 }}>
        Brand new trackers may show no Top list until candidates are discovered and the next hourly snapshot is taken.
      </div>
    </div>
  );
}
