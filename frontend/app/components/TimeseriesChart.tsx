"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export type TimeSeriesPoint = {
  captured_at: string;
  value: number | null;
};

function formatCompactNumber(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return `${value}`;
}

export function TimeseriesChart({
  points,
  valueLabel = "views",
}: {
  points: TimeSeriesPoint[];
  valueLabel?: string;
}) {
  const data = points
    .filter((p) => p.value !== null)
    .map((p) => ({
      captured_at: p.captured_at,
      value: p.value as number,
    }));

  if (data.length === 0) {
    return <div className="text-sm text-yt-muted">No time series data yet.</div>;
  }

  return (
    <div className="h-48 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="4 4" opacity={0.25} />
          <XAxis
            dataKey="captured_at"
            tickFormatter={(iso) => {
              const date = new Date(iso);
              return `${date.getDate()}/${date.getMonth() + 1} ${date.getHours()}:00`;
            }}
            minTickGap={24}
          />
          <YAxis tickFormatter={(v) => formatCompactNumber(v)} width={60} />
          <Tooltip
            labelFormatter={(iso) => new Date(iso).toLocaleString()}
            formatter={(v) => [formatCompactNumber(Number(v)), valueLabel]}
          />
          <Line type="monotone" dataKey="value" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
