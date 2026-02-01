export const metadata = {
  title: "YouTube Tracker Analytics",
  description: "Self-hosted YouTube tracking dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif", margin: 0 }}>
        <div style={{ padding: 16, borderBottom: "1px solid #eee" }}>
          <h2 style={{ margin: 0 }}>YouTube Tracker Analytics</h2>
          <div style={{ color: "#666", marginTop: 4, fontSize: 14 }}>
            Minimal UI — create trackers and view Top N
          </div>
        </div>
        <div style={{ padding: 16 }}>{children}</div>
      </body>
    </html>
  );
}
