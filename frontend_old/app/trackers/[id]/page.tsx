"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

type VideoTopItem = {
  video_id: string;
  title?: string | null;
  channel_id?: string | null;
  score: number;
  latest_view_count?: number | null;
  latest_like_count?: number | null;
  latest_comment_count?: number | null;
  published_at?: string | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function TrackerDetailPage() {
  const params = useParams();
  const trackerId = params?.id as string;

  const [items, setItems] = useState<VideoTopItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function fetchTopVideos(): Promise<void> {
    setLoading(true);
    setErrorMessage(null);

    try {
      const response = await fetch(`${API_BASE}/trackers/${trackerId}/top`);
      const data = await response.json();
      if (!response.ok) throw new Error(data?.detail || `HTTP ${response.status}`);
      setItems(data);
    } catch (error: any) {
      setErrorMessage(error?.message || "Failed to load top videos");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchTopVideos();
  }, [trackerId]);

  return (
    <div style={{ display: "grid", gap: 12, maxWidth: 980 }}>
      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <Link href="/trackers">← Back</Link>
        <h3 style={{ margin: 0 }}>Tracker #{trackerId}</h3>
        <button
          onClick={fetchTopVideos}
          style={{ marginLeft: "auto", padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd" }}
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div>Loading…</div>
      ) : errorMessage ? (
        <div style={{ color: "crimson" }}>{errorMessage}</div>
      ) : items.length === 0 ? (
        <div>No results yet. Wait for discovery + next hourly snapshot.</div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ borderCollapse: "collapse", width: "100%" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", borderBottom: "1px solid #eee", padding: 8 }}>Rank</th>
                <th style={{ textAlign: "left", borderBottom: "1px solid #eee", padding: 8 }}>Title</th>
                <th style={{ textAlign: "right", borderBottom: "1px solid #eee", padding: 8 }}>Score</th>
                <th style={{ textAlign: "right", borderBottom: "1px solid #eee", padding: 8 }}>Views</th>
                <th style={{ textAlign: "right", borderBottom: "1px solid #eee", padding: 8 }}>Likes</th>
                <th style={{ textAlign: "right", borderBottom: "1px solid #eee", padding: 8 }}>Comments</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, index) => (
                <tr key={item.video_id}>
                  <td style={{ padding: 8, borderBottom: "1px solid #f3f3f3" }}>{index + 1}</td>
                  <td style={{ padding: 8, borderBottom: "1px solid #f3f3f3" }}>
                    <div style={{ fontWeight: 600 }}>{item.title || item.video_id}</div>
                    <div style={{ color: "#666", fontSize: 12 }}>
                      <a href={`https://www.youtube.com/watch?v=${item.video_id}`} target="_blank" rel="noreferrer">
                        open on YouTube
                      </a>
                    </div>
                  </td>
                  <td style={{ padding: 8, borderBottom: "1px solid #f3f3f3", textAlign: "right" }}>{item.score.toFixed(2)}</td>
                  <td style={{ padding: 8, borderBottom: "1px solid #f3f3f3", textAlign: "right" }}>{item.latest_view_count ?? "-"}</td>
                  <td style={{ padding: 8, borderBottom: "1px solid #f3f3f3", textAlign: "right" }}>{item.latest_like_count ?? "-"}</td>
                  <td style={{ padding: 8, borderBottom: "1px solid #f3f3f3", textAlign: "right" }}>{item.latest_comment_count ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
