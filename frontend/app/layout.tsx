import "./globals.css";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata = {
  title: "YouTube Tracker Analytics",
  description: "Self-hosted YouTube tracking dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <header className="sticky top-0 z-10 border-b border-yt-border bg-yt-bg/90 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-yt-surface2 border border-yt-border" />
              <div>
                <div className="text-base font-semibold leading-tight">YouTube Tracker Analytics</div>
                <div className="text-xs text-yt-muted">Track channel top videos + momentum</div>
              </div>
            </div>
            <div className="text-xs text-yt-muted">Self-hosted</div>
          </div>
        </header>

        <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
