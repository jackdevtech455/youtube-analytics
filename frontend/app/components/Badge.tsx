export function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-full border border-yt-border bg-yt-surface2 px-2 py-0.5 text-xs text-yt-muted">
      {children}
    </span>
  );
}
