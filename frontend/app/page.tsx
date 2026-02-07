export const dynamic = "force-dynamic";
export const revalidate = 0;

import Link from "next/link";
import { Card } from "./components/Card";
import { Button } from "./components/Button";

export default function HomePage() {
  return (
    <div className="grid gap-6">
      <Card>
        <div className="grid gap-2">
          <h1 className="text-xl font-semibold">YouTube Tracker Analytics</h1>
          <p className="text-sm text-yt-muted">
            Track top videos for channels or search terms, snapshot hourly, and spot momentum early.
          </p>

          <div className="mt-3 flex flex-wrap gap-2">
            <Link href="/trackers">
              <Button>Open trackers</Button>
            </Link>
            <a
              className="text-sm text-yt-muted hover:text-yt-text underline underline-offset-2"
              href="/api/docs"
              target="_blank"
              rel="noreferrer"
            >
              API docs
            </a>
          </div>
        </div>
      </Card>

      <div className="text-xs text-yt-muted">
        Tip: brand new trackers may show no top list until candidates are discovered and the next snapshot is taken.
      </div>
    </div>
  );
}
