"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { Badge } from "../../components/Badge";
import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { TimeseriesChart, TimeSeriesPoint } from "../../components/TimeseriesChart";
import { useChannelMeta } from "../../hooks/useChannelMeta";

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

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "/api";

export default function TrackerDetailPage() {
  const params = useParams();
  const trackerId = params?.id as string;

  const [items, setItems] = useState<VideoTopItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [timeseriesByVideoId, setTimeseriesByVideoId] = useState<Record<string, TimeSeriesPoint[]>>({});
  const [loadingSeriesByVideoId, setLoadingSeriesByVideoId] = useState<Record<string, boolean>>({});

  const videoChannelIds = useMemo(() => items.map((item) => item.channel_id), [items]);
  const { metaById: channelMetaById } = useChannelMeta(videoChannelIds);

  const topVideoId = useMemo(() => items[0]?.video_id ?? null, [items]);

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

  async function ensureTimeseriesLoaded(videoId: string): Promise<void> {
    if (timeseriesByVideoId[videoId]) return;
    if (loadingSeriesByVideoId[videoId]) return;

    setLoadingSeriesByVideoId((prev) => ({ ...prev, [videoId]: true }));
    try {
      const response = await fetch(
        `${API_BASE}/videos/${videoId}/timeseries?metric=view_count&days=7`
      );
      const data = await response.json();
      if (!response.ok) throw new Error(data?.detail || `HTTP ${response.status}`);

      setTimeseriesByVideoId((prev) => ({ ...prev, [videoId]: data }));
    } catch {
      setTimeseriesByVideoId((prev) => ({ ...prev, [videoId]: [] }));
    } finally {
      setLoadingSeriesByVideoId((prev) => ({ ...prev, [videoId]: false }));
    }
  }

  useEffect(() => {
    fetchTopVideos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trackerId]);

  // Prefetch the top row series so it shows by default
  useEffect(() => {
    if (topVideoId) {
      ensureTimeseriesLoaded(topVideoId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [topVideoId]);

  return (
    <div className="grid gap-4">
      <div className="flex items-center gap-3">
        <Link className="text-sm text-yt-muted hover:text-yt-text" href="/trackers">
          ← Back
        </Link>
        <h1 className="text-lg font-semibold">Tracker #{trackerId}</h1>

        <div className="ml-auto">
          <Button variant="ghost" onClick={fetchTopVideos}>
            Refresh
          </Button>
        </div>
      </div>

      {loading ? (
        <Card>
          <div className="text-sm text-yt-muted">Loading…</div>
        </Card>
      ) : errorMessage ? (
        <Card>
          <div className="rounded-lg border border-red-600/50 bg-red-950/40 p-3 text-sm text-red-200">
            {errorMessage}
          </div>
        </Card>
      ) : items.length === 0 ? (
        <Card>
          <div className="text-sm text-yt-muted">
            No results yet. Wait for discovery + the next hourly snapshot.
          </div>
        </Card>
      ) : (
        <div className="grid gap-3">
          {items.map((item, index) => {
            const isTopRow = index === 0;
            const series = timeseriesByVideoId[item.video_id];
            const isSeriesLoading = !!loadingSeriesByVideoId[item.video_id];

            const channelMeta =
              item.channel_id ? channelMetaById[item.channel_id] : undefined;

            const channelLine = item.channel_id
              ? `${channelMeta?.handle || item.channel_id}${channelMeta?.title ? ` • ${channelMeta.title}` : ""}`
              : "unknown channel";

            return (
              <Card key={item.video_id}>
                <details
                  open={isTopRow}
                  onToggle={(event) => {
                    const detailsElement = event.currentTarget;
                    if (detailsElement.open) {
                      ensureTimeseriesLoaded(item.video_id);
                    }
                  }}
                >
                  <summary className="cursor-pointer list-none">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <div className="text-sm font-semibold">#{index + 1}</div>
                          {isTopRow && <Badge>TOP</Badge>}
                          <div className="text-sm text-yt-muted">
                            Score: {item.score.toFixed(2)}
                          </div>
                        </div>

                        <div className="mt-1 truncate text-base font-medium">
                          {item.title || item.video_id}
                        </div>

                        <div className="mt-1 truncate text-xs text-yt-muted">
                          {channelLine}
                        </div>

                        <div className="mt-2 flex flex-wrap gap-3 text-xs text-yt-muted">
                          <span>Views: {item.latest_view_count ?? "-"}</span>
                          <span>Likes: {item.latest_like_count ?? "-"}</span>
                          <span>Comments: {item.latest_comment_count ?? "-"}</span>
                          <a
                            className="hover:text-yt-text underline underline-offset-2"
                            href={`https://www.youtube.com/watch?v=${item.video_id}`}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Open on YouTube
                          </a>
                        </div>
                      </div>

                      <div className="text-xs text-yt-muted">
                        {isTopRow ? "Chart shown" : "Expand for chart"}
                      </div>
                    </div>
                  </summary>

                  <div className="mt-4 border-t border-yt-border pt-4">
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <div className="text-sm font-medium">
                        Views over time (last 7 days)
                      </div>
                      <div className="text-xs text-yt-muted">
                        hourly snapshots
                      </div>
                    </div>

                    {isSeriesLoading ? (
                      <div className="text-sm text-yt-muted">Loading chart…</div>
                    ) : (
                      <TimeseriesChart points={series ?? []} valueLabel="views" />
                    )}
                  </div>
                </details>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
