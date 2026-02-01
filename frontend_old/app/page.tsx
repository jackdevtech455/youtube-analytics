import Link from "next/link";

export default function HomePage() {
  return (
    <div style={{ display: "grid", gap: 12, maxWidth: 760 }}>
      <p>
        Create trackers for channels or search terms, then view the computed Top N.
        Channel discovery runs hourly; search discovery runs daily; snapshots run hourly.
      </p>
      <Link href="/trackers">Go to Trackers →</Link>
    </div>
  );
}
