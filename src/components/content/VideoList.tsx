import type { Video } from "@/lib/content-schema";
import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { VideoCard } from "./VideoCard";

/** The "Watch" row under a section: one card per video. */
export function VideoList({ videos, sectionId, lang }: { videos: Video[]; sectionId: string; lang: Lang }) {
  if (!videos.length) return null;
  const headingId = `${sectionId}-videos`;
  return (
    <details className="border-t border-border pt-6">
      <summary className="cursor-pointer py-2 marker:text-accent">
        <h3
          id={headingId}
          className="inline font-mono text-xs font-medium uppercase tracking-[0.16em] text-text-faint"
        >
          {UI[lang].watch(videos.length)}
        </h3>
      </summary>
      <ul className="mt-3 grid list-none gap-3 p-0 sm:grid-cols-2">
        {videos.map((video) => (
          <li key={video.id}>
            <VideoCard video={video} lang={lang} />
          </li>
        ))}
      </ul>
    </details>
  );
}
