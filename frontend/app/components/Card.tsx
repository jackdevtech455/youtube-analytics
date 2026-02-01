export function Card({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-yt-border bg-yt-surface p-4 shadow-sm">
      {children}
    </div>
  );
}
