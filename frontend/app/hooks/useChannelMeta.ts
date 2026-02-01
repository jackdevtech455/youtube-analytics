"use client";

import { useEffect, useMemo, useState } from "react";

export type ChannelMeta = {
  channel_id: string;
  title?: string | null;
  handle?: string | null;
  thumbnail_url?: string | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export function useChannelMeta(channelIds: Array<string | null | undefined>) {
  const uniqueIds = useMemo(() => {
    const ids = channelIds
      .filter((id): id is string => typeof id === "string" && id.trim().length > 0)
      .map((id) => id.trim());
    return Array.from(new Set(ids));
  }, [channelIds]);

  const [metaById, setMetaById] = useState<Record<string, ChannelMeta>>({});
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const missingIds = uniqueIds.filter((id) => !metaById[id]);
    if (missingIds.length === 0) return;

    let cancelled = false;

    async function loadMissing(): Promise<void> {
      setLoading(true);
      try {
        const chunkSize = 40;
        for (let index = 0; index < missingIds.length; index += chunkSize) {
          const chunkIds = missingIds.slice(index, index + chunkSize);
          const response = await fetch(
            `${API_BASE}/channels/meta?ids=${encodeURIComponent(chunkIds.join(","))}`
          );
          const data = await response.json();
          if (!response.ok) throw new Error(data?.detail || `HTTP ${response.status}`);

          if (cancelled) return;

          const mapped: Record<string, ChannelMeta> = {};
          for (const item of data as ChannelMeta[]) {
            mapped[item.channel_id] = item;
          }
          setMetaById((prev) => ({ ...prev, ...mapped }));
        }
      } catch {
        // fail silently; UI will fall back to channel_id
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadMissing();

    return () => {
      cancelled = true;
    };
  }, [uniqueIds, metaById]);

  return { metaById, loading };
}
