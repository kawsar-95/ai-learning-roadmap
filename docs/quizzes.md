# Writing a quiz for a topic

A topic shows a quiz when its file in `src/content/` has a `quiz` list. A topic
without `quiz` shows no quiz, no "Go to quiz" link, and no score on the
dashboard. Aim for 5 questions in each topic.

## Where to put it

Add `quiz` at the top level of the topic file, next to `sections` and
`sources`:

```json
{
  "slug": "inference",
  "title": "Inference",
  "sections": [ ... ],
  "sources": [ ... ],
  "quiz": [ ... ]
}
```

## The two question types

Multiple choice (`mcq`). `answer` is the index of the right option, starting
at 0. The English and Bangla lists must have the same number of options, in the
same order.

```json
{
  "id": "q1",
  "kind": "mcq",
  "answer": 1,
  "en": {
    "q": "Which server is known for PagedAttention?",
    "options": ["Ollama", "vLLM", "llama.cpp"],
    "why": "vLLM uses PagedAttention to use GPU memory well."
  },
  "bn": {
    "q": "কোন server PagedAttention-এর জন্য পরিচিত?",
    "options": ["Ollama", "vLLM", "llama.cpp"],
    "why": "vLLM GPU memory ভালোভাবে কাজে লাগাতে PagedAttention ব্যবহার করে।"
  }
}
```

True or false (`tf`). `answer` is `true` or `false`. There are no options.

```json
{
  "id": "q2",
  "kind": "tf",
  "answer": false,
  "en": { "q": "Self-hosting is always cheaper than a hosted API.", "why": "It depends on how much traffic you have." },
  "bn": { "q": "Self-host করা সবসময় hosted API-এর চেয়ে সস্তা।", "why": "এটা তোমার traffic-এর উপর নির্ভর করে।" }
}
```

## Rules

The build fails with a clear error if a quiz breaks one of these rules.

- Every `id` is different inside one topic.
- The text is plain text. HTML is not allowed. No text may be empty.
- An `mcq` has 2 to 6 options. Its `answer` is a valid index.
- The `en` and `bn` of an `mcq` have the same number of options.
- A `tf` has a `true` or `false` answer.
- The `quiz` list is not empty. To remove a quiz, remove the `quiz` key.
- No other keys are allowed.

Write the `why` text for the right answer. The reader sees it after checking.

## What the reader sees

- At the end of the topic page, before the sources: the questions, a "Check
  answers" button that works after every question has an answer, the score,
  and "Try again".
- A "5 questions" pill and a "Go to quiz" link in the topic header.
- The best score of each topic, saved in the browser, on the dashboard.

If you change the number of questions, the saved best score for that topic is
not shown until the reader takes the quiz again.
