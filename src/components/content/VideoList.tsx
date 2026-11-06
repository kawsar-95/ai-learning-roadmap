import type { Video } from "@/lib/content-schema";
import { UI } from "@/lib/i18n";
import type { Lang } from "@/lib/i18n";
import { VideoCard } from "./VideoCard";

/** The "Watch" row under a section: the video cards, then the Shorts in their own vertical grid. */
export function VideoList({ videos, sectionId, lang }: { videos: Video[]; sectionId: string; lang: Lang }) {
  if (!videos.length) return null;
  const headingId = `${sectionId}-videos`;
  const full = videos.filter((video) => video.format !== "short");
  const shorts = videos.filter((video) => video.format === "short");
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
      {full.length > 0 && (
        <ul className="mt-3 grid list-none gap-3 p-0 sm:grid-cols-2">
          {full.map((video) => (
            <li key={video.id}>
              <VideoCard video={video} lang={lang} />
            </li>
          ))}
        </ul>
      )}
      {shorts.length > 0 && (
        <>
          {full.length > 0 && (
            <h4 className="mt-5 font-mono text-xs font-medium uppercase tracking-[0.16em] text-text-faint">
              {UI[lang].shorts}
            </h4>
          )}
          <ul className="mt-3 grid list-none grid-cols-[repeat(auto-fill,minmax(min(100%,12.5rem),1fr))] gap-3 p-0">
            {shorts.map((video) => (
              <li key={video.id}>
                <VideoCard video={video} lang={lang} />
              </li>
            ))}
          </ul>
        </>
      )}
    </details>
  );
}
