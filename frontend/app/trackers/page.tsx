"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Badge } from "../components/Badge";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { Input } from "../components/Input";
import { Select } from "../components/Select";
import { useChannelMeta } from "../hooks/useChannelMeta";
import type { SelectOption } from "../components/Select";

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

const trackerTypeOptions = [
  { value: "channel", label: "Channel (hourly discovery)" },
  { value: "search", label: "Search (daily discovery)" },
] as const satisfies ReadonlyArray<SelectOption<TrackerType>>;

const rankingMetricOptions = [
  { value: "views", label: "Views (latest)" },
  { value: "likes", label: "Likes (latest)" },
  { value: "comments", label: "Comments (latest)" },
  { value: "views_delta", label: "Views delta (window)" },
  { value: "views_velocity", label: "Views/hour velocity (window)" },
  { value: "likes_delta", label: "Likes delta (window)" },
  { value: "comments_delta", label: "Comments delta (window)" },
] as const satisfies ReadonlyArray<SelectOption<RankingMetric>>;

export default function TrackersPage() {
  const [trackers, setTrackers] = useState<Tracker[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [trackerType, setTrackerType] = useState<TrackerType>("channel");
  const [channelIdentifier, setChannelIdentifier] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const [topN, setTopN] = useState<number>(20);
  const [poolSize, setPoolSize] = useState<number>(200);

  const [rankingMetric, setRankingMetric] = useState<RankingMetric>("views");
  const [windowHours, setWindowHours] = useState<number>(24);

  const rankingNeedsWindow = useMemo(
    () => rankingMetric.includes("delta") || rankingMetric.includes("velocity"),
    [rankingMetric]
  );

  const channelIds = useMemo(
    () => trackers.filter((t) => t.type === "channel").map((t) => t.channel_id),
    [trackers]
  );
  const { metaById: channelMetaById } = useChannelMeta(channelIds);

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

    if (trackerType === "channel") payload.channel_id = channelIdentifier.trim();
    if (trackerType === "search") payload.search_query = searchQuery.trim();

    try {
      const response = await fetch(`${API_BASE}/trackers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data?.detail || `HTTP ${response.status}`);

      setChannelIdentifier("");
      setSearchQuery("");
      await fetchTrackers();
    } catch (error: any) {
      setErrorMessage(error?.message || "Failed to create tracker");
    }
  }

  return (
    <div className="grid gap-4">
      <div className="flex items-center gap-3">
        <Link className="text-sm text-yt-muted hover:text-yt-text" href="/">
          ← Home
        </Link>
        <h1 className="text-lg font-semibold">Trackers</h1>
        <div className="ml-auto">
          <Button variant="ghost" onClick={fetchTrackers}>
            Refresh
          </Button>
        </div>
      </div>

      <Card>
        <div className="grid gap-3">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-base font-semibold">Create tracker</div>
              <div className="text-xs text-yt-muted">
                Channel trackers: hourly discovery. Search trackers: daily discovery. All snapshots hourly.
              </div>
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <div className="grid gap-1">
              <div className="text-xs text-yt-muted">Type</div>
              <Select<TrackerType>
                value={trackerType}
                onChange={setTrackerType}
                options={trackerTypeOptions}
              />
            </div>

            {trackerType === "channel" ? (
              <div className="grid gap-1">
                <div className="text-xs text-yt-muted">Channel</div>
                <Input
                  value={channelIdentifier}
                  onChange={setChannelIdentifier}
                  placeholder="UC... OR @handle OR https://youtube.com/@handle"
                />
                <div className="text-xs text-yt-muted">
                  You can paste a handle and the backend will resolve it to a channel ID.
                </div>
              </div>
            ) : (
              <div className="grid gap-1">
                <div className="text-xs text-yt-muted">Search query</div>
                <Input
                  value={searchQuery}
                  onChange={setSearchQuery}
                  placeholder='e.g. "van build timelapse"'
                />
              </div>
            )}
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            <div className="grid gap-1">
              <div className="text-xs text-yt-muted">Top N</div>
              <Input
                value={String(topN)}
                onChange={(value) => setTopN(parseInt(value || "20", 10))}
                type="number"
              />
            </div>
            <div className="grid gap-1">
              <div className="text-xs text-yt-muted">Candidate pool size</div>
              <Input
                value={String(poolSize)}
                onChange={(value) => setPoolSize(parseInt(value || "200", 10))}
                type="number"
              />
            </div>
            <div className="grid gap-1">
              <div className="text-xs text-yt-muted">Ranking metric</div>
              <Select<RankingMetric>
                value={rankingMetric}
                onChange={setRankingMetric}
                options={rankingMetricOptions}
              />
            </div>
          </div>

          {rankingNeedsWindow && (
            <div className="grid gap-1">
              <div className="text-xs text-yt-muted">Window hours</div>
              <div className="flex flex-wrap items-center gap-2">
                <div className="w-40">
                  <Input
                    value={String(windowHours)}
                    onChange={(value) => setWindowHours(parseInt(value || "24", 10))}
                    type="number"
                  />
                </div>
                <div className="text-xs text-yt-muted">(24 = 1 day, 168 = 7 days)</div>
              </div>
            </div>
          )}

          {errorMessage && (
            <div className="rounded-lg border border-red-600/50 bg-red-950/40 p-3 text-sm text-red-200">
              {errorMessage}
            </div>
          )}

          <div className="flex justify-end">
            <Button onClick={createTracker}>Create</Button>
          </div>
        </div>
      </Card>

      <div className="grid gap-3">
        {loading ? (
          <Card>
            <div className="text-sm text-yt-muted">Loading…</div>
          </Card>
        ) : trackers.length === 0 ? (
          <Card>
            <div className="text-sm text-yt-muted">No trackers yet.</div>
          </Card>
        ) : (
          trackers.map((tracker) => {
            const channelMeta =
              tracker.type === "channel" && tracker.channel_id
                ? channelMetaById[tracker.channel_id]
                : undefined;

            const trackerTitle =
              tracker.type === "channel"
                ? channelMeta?.handle || tracker.channel_id || "channel"
                : tracker.search_query || "search";

            const trackerSubtitle =
              tracker.type === "channel"
                ? channelMeta?.title || ""
                : "Search tracker";

            return (
              <Card key={tracker.id}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-semibold">#{tracker.id}</div>
                      <Badge>{tracker.type.toUpperCase()}</Badge>
                      {tracker.is_active ? <Badge>ACTIVE</Badge> : <Badge>PAUSED</Badge>}
                    </div>

                    <div className="mt-1 truncate text-base font-medium">{trackerTitle}</div>
                    {trackerSubtitle ? (
                      <div className="mt-1 truncate text-xs text-yt-muted">{trackerSubtitle}</div>
                    ) : null}

                    <div className="mt-2 text-xs text-yt-muted">
                      top_n={tracker.top_n}, pool={tracker.candidate_pool_size}, metric={tracker.ranking_metric}
                      {tracker.ranking_window_hours ? ` (${tracker.ranking_window_hours}h)` : ""}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Link href={`/trackers/${tracker.id}`}>
                      <Button variant="ghost">View →</Button>
                    </Link>
                  </div>
                </div>
              </Card>
            );
          })
        )}
      </div>

      <div className="text-xs text-yt-muted">
        Brand new trackers may show no Top list until candidates are discovered and the next hourly snapshot is taken.
      </div>
    </div>
  );
}
