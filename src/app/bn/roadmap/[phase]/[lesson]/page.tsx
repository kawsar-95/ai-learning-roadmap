import { LessonPage, lessonMetadata, lessonStaticParams } from "@/components/pages/LessonPage";
import type { LessonParams } from "@/components/pages/LessonPage";

export const dynamicParams = false;
export const generateStaticParams = lessonStaticParams;

export function generateMetadata({ params }: { params: Promise<LessonParams> }) {
  return lessonMetadata(params);
}

export default function Page({ params }: { params: Promise<LessonParams> }) {
  return <LessonPage params={params} lang="bn" />;
}
