import { z } from "zod";

export type Inline = string;
export type CalloutVariant = "info" | "good" | "warn" | "danger" | "pink";

export type Block =
  | { type: "paragraph"; html: Inline }
  | { type: "heading"; level: 3 | 4; id: string; html: Inline }
  | { type: "list"; ordered: boolean; items: Inline[] }
  | { type: "code"; lang: string; code: string; html: string }
  | { type: "diagram"; svg: string; caption?: Inline; captionBn?: Inline }
  | { type: "callout"; variant: CalloutVariant; blocks: Block[] }
  | { type: "analogy"; blocks: Block[] }
  | { type: "pillGrid"; items: { label: Inline; value: Inline }[] }
  | { type: "table"; headers: Inline[]; rows: Inline[][] }
  | { type: "panels"; panels: { heading: Inline; blocks: Block[] }[] }
  | { type: "divider" }
  | { type: "html"; html: string };

export type Video = {
  id: string;
  title: string;
  channel: string;
  lang: "en" | "bn";
  /** "short" for a vertical YouTube Short (9:16). Leave it out for a normal 16:9 video. */
  format?: "short";
  /** The length in whole seconds, shown on the card. Leave it out when unknown. */
  seconds?: number;
};

/** The longest YouTube Short, in seconds. */
export const MAX_SHORT_SECONDS = 180;

/**
 * The hosts a section may show or link to. A page on FRAMEABLE_HOSTS can be
 * shown in a frame. A page on LINK_ONLY_HOSTS sends a header that blocks
 * framing, so the site only links to it.
 */
export const FRAMEABLE_HOSTS: readonly string[] = [
  "poloclub.github.io",
  "bbycroft.net",
  "jalammar.github.io",
  "playground.tensorflow.org",
  "handbook.modular.com",
  "www.neuronpedia.org",
  "apple.github.io",
  "www.3blue1brown.com",
  "sebastianraschka.com",
];
export const LINK_ONLY_HOSTS: readonly string[] = [
  "magazine.sebastianraschka.com",
  "newsletter.maartengrootendorst.com",
  "designed-to-scale.vercel.app",
];

/** The host of an https URL, or null for any other URL. */
export function httpsHost(url: string): string | null {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" ? parsed.hostname : null;
  } catch {
    return null;
  }
}

export function canFrameUrl(url: string): boolean {
  const host = httpsHost(url);
  return host !== null && FRAMEABLE_HOSTS.includes(host);
}

export function isAllowedEmbedUrl(url: string): boolean {
  const host = httpsHost(url);
  return host !== null && (FRAMEABLE_HOSTS.includes(host) || LINK_ONLY_HOSTS.includes(host));
}

/** A live page from another site, shown in a frame under the section intro. */
export type Embed = {
  /** An https URL on one of the listed hosts. */
  url: string;
  title: string;
  /** What to look at, in English and in Bangla. */
  note: Inline;
  noteBn: Inline;
  /** false: the publisher blocks framing, so show a link card only. */
  frame?: boolean;
  /** Load the frame when it scrolls into view. Use it only for light pages. */
  autoload?: boolean;
  /** Frame height in px. */
  height?: number;
  /**
   * For an app that needs a wide screen: the width in px that it is made for.
   * In a narrower column the frame keeps this width and shrinks to fit.
   */
  designWidth?: number;
};

/** One step of a practice task, done in an AI chat. */
export type PracticeStep = {
  /** Open a new chat for this step, or keep the same one. */
  chat: "new" | "same";
  /** What to do. */
  do: Inline;
  /** Text to copy into the chat. Plain text. */
  prompt?: string;
  /** What the reader should see after this step. */
  expect: Inline;
  /** A sample AI answer. Plain text. Real answers differ a little. */
  example?: string;
};

/** A practice task in one language. */
export type PracticeText = {
  title: string;
  why: Inline;
  steps: PracticeStep[];
  learned: Inline;
  done: Inline;
  check: { question: Inline; answer: Inline };
  challenge: Inline;
};

/** A hands-on task that a reader does in any free AI chat, in English and Bangla. */
export type Practice = { en: PracticeText; bn: PracticeText };

/** A word the section uses, and what it means in plain words. */
export type BasicsWord = { term: Inline; meaning: Inline };

/** The "Start here" box of a section in one language. */
export type BasicsText = {
  /** The big idea of the section, in one to three plain sentences. */
  idea: Inline;
  /** The words of the section that a beginner may not know, in reading order. */
  words: BasicsWord[];
  /** The few points to take away. */
  remember: Inline[];
};

/**
 * A plain-words start to a section, in English and Bangla. It shows above
 * every voice, so the reader meets the words before the text uses them.
 */
export type Basics = { en: BasicsText; bn: BasicsText };

/** A short label in English and Bangla. Plain text. */
export type Bilingual = { en: string; bn: string };

/** The kind of a box in a walk-through diagram. It picks the icon. */
export const WALK_NODE_KINDS = [
  "user",
  "browser",
  "dns",
  "server",
  "database",
  "cache",
  "cdn",
  "balancer",
  "queue",
  "storage",
  "service",
  "lock",
  "key",
  "shield",
  "clock",
  "chart",
  "file",
  "note",
] as const;
export type WalkNodeKind = (typeof WALK_NODE_KINDS)[number];

/** A box of a walk-through diagram, at its home position in the scene. */
export type WalkNode = { id: string; kind: WalkNodeKind; label: Bilingual; x: number; y: number };

/** How a box looks in one step. A box that a step does not list is hidden. */
export type WalkShow = {
  id: string;
  /** hot: the step is about it. warn: slow or failing. dim: there, but not in focus. */
  state?: "hot" | "warn" | "dim";
  /** A small second line, such as a time or a place. */
  sub?: Bilingual;
  /** A count in a corner, such as "×40". */
  badge?: string;
  /** A position for this step only, when the box moves. */
  x?: number;
  y?: number;
};

/** A line between two shown boxes. With `flow`, dots travel along it. */
export type WalkLink = {
  from: string;
  to: string;
  /** to: dots go from `from` to `to`. back: the other way. both: there and back. */
  flow?: "to" | "back" | "both";
  /** How long one dot takes to cross, in ms. A slow link has slow dots. */
  ms?: number;
  state?: "hot" | "warn" | "dim";
  label?: Bilingual;
};

/** The words of one walk-through step in one language. No links or citations: the section text has them. */
export type WalkText = {
  /** The label on the step strip. */
  short: string;
  title: string;
  body: Inline[];
  note?: { kind: "insight" | "tip" | "warn"; html: Inline };
  /** What the step added (+), took away (-) or changed (~). */
  changes?: { sign: "+" | "-" | "~"; html: Inline }[];
  /** The points to take away, for a recap step. */
  points?: Inline[];
};

export type WalkStep = {
  en: WalkText;
  bn: WalkText;
  show: WalkShow[];
  links: WalkLink[];
  /**
   * One value per readout. A string is the same in both languages (its digits
   * turn Bangla on the Bangla site). null shows a dash.
   */
  values?: (string | Bilingual | null)[];
};

/**
 * A step-by-step walk-through of a section: a diagram that changes with each
 * step, a row of readouts, and the words of each step in English and Bangla.
 */
export type Walkthrough = {
  /** The size of the diagram, in diagram units. */
  width: number;
  height: number;
  nodes: WalkNode[];
  /** The labels of the readouts above the diagram. */
  metrics: Bilingual[];
  /** A line under the readouts, for example to say that the numbers are an example. */
  caption?: Bilingual;
  steps: WalkStep[];
};

export type Section = {
  id: string;
  num: string;
  title: string;
  sub: Inline;
  /** The Bangla title and intro, for the Bangla site. */
  bn: { title: string; sub: Inline };
  basics?: Basics;
  walkthrough?: Walkthrough;
  body: Block[];
  layman: Block[];
  bangla: Block[];
  videos?: Video[];
  embeds?: Embed[];
  practice?: Practice[];
};

export type Source = { n: number; url: string; text: string };

type McqText = { q: string; options: string[]; why: string };
type TfText = { q: string; why: string };
/** One quiz question. `mcq` has one right option (an index); `tf` is true or false. */
export type QuizQuestion =
  | { id: string; kind: "mcq"; answer: number; en: McqText; bn: McqText }
  | { id: string; kind: "tf"; answer: boolean; en: TfText; bn: TfText };

export type TopicFile = {
  slug: string;
  title: string;
  tagline?: string;
  lede: Inline;
  /** The Bangla title, tagline, and intro, for the Bangla site. */
  bn: { title: string; tagline?: string; lede: Inline };
  sections: Section[];
  sources: Source[];
  /** The quiz at the end of the topic page. Leave it out for no quiz. */
  quiz?: QuizQuestion[];
};

const TAG = /<[^>]*>/g;
const ALLOWED_TAGS: RegExp[] = [
  /^<\/?(strong|em|code)>$/,
  /^<br\s*\/?>$/,
  /^<a class="cite" href="#src\d+">$/,
  /^<a href="https?:\/\/[^"\s<>]+">$/,
  /^<\/a>$/,
];

export function isAllowedInline(html: string): boolean {
  const tags = html.match(TAG) ?? [];
  if (!tags.every((tag) => ALLOWED_TAGS.some((re) => re.test(tag)))) return false;
  return !html.replace(TAG, "").includes("<");
}

const InlineSchema = z.string().refine(isAllowedInline, {
  message: "Inline html uses a tag or attribute outside the allowlist",
});

const CalloutVariantSchema = z.enum(["info", "good", "warn", "danger", "pink"]);

export const BlockSchema: z.ZodType<Block> = z.lazy(() =>
  z.discriminatedUnion("type", [
    z.strictObject({ type: z.literal("paragraph"), html: InlineSchema }),
    z.strictObject({
      type: z.literal("heading"),
      level: z.union([z.literal(3), z.literal(4)]),
      id: z.string(),
      html: InlineSchema,
    }),
    z.strictObject({
      type: z.literal("list"),
      ordered: z.boolean(),
      items: z.array(InlineSchema),
    }),
    z.strictObject({
      type: z.literal("code"),
      lang: z.string(),
      code: z.string(),
      html: z.string(),
    }),
    z.strictObject({
      type: z.literal("diagram"),
      svg: z.string(),
      caption: InlineSchema.optional(),
      captionBn: InlineSchema.optional(),
    }),
    z.strictObject({
      type: z.literal("callout"),
      variant: CalloutVariantSchema,
      blocks: z.array(BlockSchema),
    }),
    z.strictObject({ type: z.literal("analogy"), blocks: z.array(BlockSchema) }),
    z.strictObject({
      type: z.literal("pillGrid"),
      items: z.array(z.strictObject({ label: InlineSchema, value: InlineSchema })),
    }),
    z.strictObject({
      type: z.literal("table"),
      headers: z.array(InlineSchema),
      rows: z.array(z.array(InlineSchema)),
    }),
    z.strictObject({
      type: z.literal("panels"),
      panels: z.array(
        z.strictObject({ heading: InlineSchema, blocks: z.array(BlockSchema) }),
      ),
    }),
    z.strictObject({ type: z.literal("divider") }),
    z.strictObject({ type: z.literal("html"), html: z.string() }),
  ]),
);

const VideoSchema = z
  .strictObject({
    id: z.string().regex(/^[A-Za-z0-9_-]{11}$/, "Expected an 11-character YouTube video id"),
    title: z.string().min(1),
    channel: z.string().min(1),
    lang: z.enum(["en", "bn"]),
    format: z.literal("short").optional(),
    seconds: z.number().int().positive().optional(),
  })
  .refine((v) => v.format !== "short" || v.seconds === undefined || v.seconds <= MAX_SHORT_SECONDS, {
    message: `A Short is at most ${MAX_SHORT_SECONDS} seconds long`,
  });

const FilledInlineSchema = InlineSchema.refine((s) => s.trim().length > 0, {
  message: "Expected non-empty text",
});

const PlainTextSchema = z.string().trim().min(1);

const EmbedSchema = z
  .strictObject({
    url: z.string().refine(isAllowedEmbedUrl, {
      message: "An embed needs an https URL on a host in FRAMEABLE_HOSTS or LINK_ONLY_HOSTS",
    }),
    title: PlainTextSchema,
    note: FilledInlineSchema,
    noteBn: FilledInlineSchema,
    frame: z.boolean().optional(),
    autoload: z.boolean().optional(),
    height: z.number().int().min(320).max(1000).optional(),
    designWidth: z.number().int().min(600).max(1600).optional(),
  })
  .refine((e) => e.frame === false || canFrameUrl(e.url), {
    message: "This host does not allow framing. Set frame to false.",
  })
  .refine((e) => !(e.autoload && e.frame === false), {
    message: "A link card has nothing to autoload",
  });

const PracticeStepSchema = z.strictObject({
  chat: z.enum(["new", "same"]),
  do: FilledInlineSchema,
  prompt: PlainTextSchema.optional(),
  expect: FilledInlineSchema,
  example: PlainTextSchema.optional(),
});

const PracticeTextSchema = z.strictObject({
  title: PlainTextSchema,
  why: FilledInlineSchema,
  steps: z
    .array(PracticeStepSchema)
    .min(1)
    .refine((steps) => steps[0]?.chat === "new", {
      message: "The first step must open a new chat",
    }),
  learned: FilledInlineSchema,
  done: FilledInlineSchema,
  check: z.strictObject({ question: FilledInlineSchema, answer: FilledInlineSchema }),
  challenge: FilledInlineSchema,
});

const PracticeSchema = z.strictObject({ en: PracticeTextSchema, bn: PracticeTextSchema });

// The box restates its section in plain words. The section text carries the
// citations, so the box has no citation and no link.
const BasicsInlineSchema = FilledInlineSchema.refine((s) => !/<a[\s>]/.test(s), {
  message: "A Start here box has no links and no citations",
});

const BasicsTextSchema = z.strictObject({
  idea: BasicsInlineSchema,
  words: z.array(z.strictObject({ term: BasicsInlineSchema, meaning: BasicsInlineSchema })).min(2).max(8),
  remember: z.array(BasicsInlineSchema).min(2).max(5),
});

const BasicsSchema = z
  .strictObject({ en: BasicsTextSchema, bn: BasicsTextSchema })
  .refine((b) => b.en.words.length === b.bn.words.length && b.en.remember.length === b.bn.remember.length, {
    message: "en and bn must have the same number of words and of points to remember",
  });

// A walk-through restates its section step by step. The section text carries
// the citations, so the steps have no citation and no link.
const WalkInlineSchema = FilledInlineSchema.refine((s) => !/<a[\s>]/.test(s), {
  message: "A walk-through step has no links and no citations",
});
const BilingualSchema = z.strictObject({ en: PlainTextSchema, bn: PlainTextSchema });

const WalkTextSchema = z.strictObject({
  short: PlainTextSchema,
  title: PlainTextSchema,
  body: z.array(WalkInlineSchema).min(1),
  note: z.strictObject({ kind: z.enum(["insight", "tip", "warn"]), html: WalkInlineSchema }).optional(),
  changes: z.array(z.strictObject({ sign: z.enum(["+", "-", "~"]), html: WalkInlineSchema })).min(1).optional(),
  points: z.array(WalkInlineSchema).min(1).optional(),
});

const WalkStepSchema = z.strictObject({
  en: WalkTextSchema,
  bn: WalkTextSchema,
  show: z
    .array(
      z.strictObject({
        id: z.string(),
        state: z.enum(["hot", "warn", "dim"]).optional(),
        sub: BilingualSchema.optional(),
        badge: PlainTextSchema.optional(),
        x: z.number().optional(),
        y: z.number().optional(),
      }),
    )
    .min(1),
  links: z.array(
    z.strictObject({
      from: z.string(),
      to: z.string(),
      flow: z.enum(["to", "back", "both"]).optional(),
      ms: z.number().int().min(200).max(10000).optional(),
      state: z.enum(["hot", "warn", "dim"]).optional(),
      label: BilingualSchema.optional(),
    }),
  ),
  values: z.array(z.union([PlainTextSchema, BilingualSchema]).nullable()).optional(),
});

const WalkthroughSchema = z
  .strictObject({
    width: z.number().int().min(320).max(1200),
    height: z.number().int().min(160).max(800),
    nodes: z
      .array(
        z.strictObject({
          id: z.string().regex(/^[a-z][a-z0-9-]*$/),
          kind: z.enum(WALK_NODE_KINDS),
          label: BilingualSchema,
          x: z.number(),
          y: z.number(),
        }),
      )
      .min(1),
    metrics: z.array(BilingualSchema).max(6),
    caption: BilingualSchema.optional(),
    steps: z.array(WalkStepSchema).min(2),
  })
  .superRefine((w, ctx) => {
    const ids = new Set<string>();
    for (const node of w.nodes) {
      if (ids.has(node.id)) ctx.addIssue({ code: "custom", message: `duplicate node id ${node.id}` });
      ids.add(node.id);
    }
    w.steps.forEach((step, i) => {
      const where = `step ${i + 1}`;
      const shown = new Set<string>();
      for (const s of step.show) {
        if (!ids.has(s.id)) ctx.addIssue({ code: "custom", message: `${where}: unknown node ${s.id}` });
        if (shown.has(s.id)) ctx.addIssue({ code: "custom", message: `${where}: ${s.id} is shown twice` });
        shown.add(s.id);
        const x = s.x ?? w.nodes.find((n) => n.id === s.id)?.x ?? 0;
        const y = s.y ?? w.nodes.find((n) => n.id === s.id)?.y ?? 0;
        if (x < 0 || x > w.width || y < 0 || y > w.height) {
          ctx.addIssue({ code: "custom", message: `${where}: ${s.id} is outside the diagram` });
        }
      }
      for (const link of step.links) {
        if (!shown.has(link.from) || !shown.has(link.to) || link.from === link.to) {
          ctx.addIssue({ code: "custom", message: `${where}: a link must join two shown boxes (${link.from} → ${link.to})` });
        }
      }
      if ((step.values?.length ?? 0) !== w.metrics.length) {
        ctx.addIssue({ code: "custom", message: `${where}: needs one value per readout` });
      }
    });
  });

export const SectionSchema: z.ZodType<Section> = z.strictObject({
  id: z.string(),
  num: z.string(),
  title: z.string(),
  sub: InlineSchema,
  bn: z.strictObject({ title: PlainTextSchema, sub: InlineSchema }),
  basics: BasicsSchema.optional(),
  walkthrough: WalkthroughSchema.optional(),
  body: z.array(BlockSchema),
  layman: z.array(BlockSchema),
  bangla: z.array(BlockSchema),
  videos: z.array(VideoSchema).optional(),
  embeds: z.array(EmbedSchema).optional(),
  practice: z.array(PracticeSchema).min(1).optional(),
});

const SourceSchema = z.strictObject({
  n: z.number(),
  url: z.string(),
  text: z.string(),
});

/** Quiz text is plain text. A tag would show as literal characters, so the build rejects it. */
// A tag is `<` then a letter or `/`, so "3 < 5 and 7 > 6" is allowed. Not `TAG`: it has the `g` flag,
// and `test` with that flag keeps state between calls.
const QuizTextSchema = PlainTextSchema.refine((text) => !/<\/?[a-zA-Z][^>]*>/.test(text), {
  message: "quiz text must be plain text, with no HTML tags",
});
const McqTextSchema = z.strictObject({
  q: QuizTextSchema,
  options: z.array(QuizTextSchema).min(2).max(6),
  why: QuizTextSchema,
});
const TfTextSchema = z.strictObject({ q: QuizTextSchema, why: QuizTextSchema });

const QuizQuestionSchema: z.ZodType<QuizQuestion> = z
  .discriminatedUnion("kind", [
    z.strictObject({
      id: PlainTextSchema,
      kind: z.literal("mcq"),
      answer: z.number().int(),
      en: McqTextSchema,
      bn: McqTextSchema,
    }),
    z.strictObject({ id: PlainTextSchema, kind: z.literal("tf"), answer: z.boolean(), en: TfTextSchema, bn: TfTextSchema }),
  ])
  .superRefine((q, ctx) => {
    if (q.kind !== "mcq") return;
    if (q.en.options.length !== q.bn.options.length) {
      ctx.addIssue({ code: "custom", message: "en and bn must have the same number of options" });
    }
    if (q.answer < 0 || q.answer >= q.en.options.length) {
      ctx.addIssue({ code: "custom", message: "answer must be an index of the options" });
    }
  });

export const TopicFileSchema: z.ZodType<TopicFile> = z.strictObject({
  slug: z.string(),
  title: z.string(),
  tagline: z.string().optional(),
  lede: InlineSchema,
  bn: z.strictObject({
    title: PlainTextSchema,
    tagline: PlainTextSchema.optional(),
    lede: InlineSchema,
  }),
  sections: z.array(SectionSchema),
  sources: z.array(SourceSchema),
  quiz: z
    .array(QuizQuestionSchema)
    .min(1)
    .refine((qs) => new Set(qs.map((q) => q.id)).size === qs.length, { message: "quiz ids must be unique" })
    .optional(),
});
