import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

// The walk-throughs of Parts 1 to 17 are built by scripts/walkthroughs (see its README): each source in
// scripts/walkthroughs/<Part>/<section>.py becomes src/content/walkthroughs/<Part>/<section>.json, and index.ts lists them.
// The JSON is what the site ships, so it has to be what the sources build. `build.py --check` writes nothing and exits 1 on a difference.
const root = fileURLToPath(new URL("..", import.meta.url));
const build = join(root, "scripts/walkthroughs/build.py");
const env = { ...process.env, PYTHONDONTWRITEBYTECODE: "1" };

const python = spawnSync("python3", ["-c", "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"], { env });
const skip = python.status === 0 ? false : "needs python3 3.10 or newer on PATH";

function run(repo: string, ...flags: string[]) {
  const r = spawnSync("python3", [build, ...flags, repo], { env, encoding: "utf8", timeout: 60_000 });
  return { status: r.status, output: `${r.stdout}${r.stderr}` };
}

// A small walk-through that passes every rule: 6 steps, two boxes, one line with a label.
const SOURCE = `from kit import walk, node, sh, ln, st

BN = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def step(i, body_bn="ধাপ {n} এর বিবরণ।", extra_show=()):
    n = str(i).translate(BN)
    return st(
        (f"Step {i}", f"ধাপ {n}"),
        (f"Title {i}", f"শিরোনাম {n}"),
        [(f"Body of step {i}.", body_bn.format(n=n, i=i))],
        [sh("a", "hot"), sh("b"), *extra_show],
        [ln("a", "b", "to", label=("asks", "চায়"))],
        values=[str(i)],
    )


WALK = walk(
    600, 220,
    [node("a", "user", ("User", "ব্যবহারকারী"), 120, 110), node("b", "server", ("Server", "সার্ভার"), 460, 110)],
    [("Step", "ধাপ")],
    None,
    [step(i) for i in range(1, 7)],
)
`;

const SLUG = "llm-fundamentals";

/** A walk-through with `total` boxes, of which the first `shown` are shown in every step. For the box-count rules. */
const boxes = (total: number, shown: number) => `from kit import walk, node, sh, st

BN = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
NODES = [node(f"n{i}", "user", ("Box", "বক্স"), 70 + 125 * (i % 9), 60 + 90 * (i // 9)) for i in range(${total})]


def step(i):
    n = str(i).translate(BN)
    return st((f"Step {i}", f"ধাপ {n}"), (f"Title {i}", f"শিরোনাম {n}"), [(f"Body {i}.", f"বিবরণ {n}।")], [sh(f"n{k}") for k in range(${shown})], [], values=[str(i)])


WALK = walk(1200, 300, NODES, [("Step", "ধাপ")], None, [step(i) for i in range(1, 7)])
`;

/** A repo with the two files the builder reads (topics.ts for the Part list, content-schema.ts for the kinds), one Part file and one source. */
function fixture(source = SOURCE, file = `${SLUG}/s1.py`) {
  const dir = mkdtempSync(join(tmpdir(), "walkthrough-builder-"));
  mkdirSync(join(dir, "src/lib"), { recursive: true });
  mkdirSync(join(dir, "src/content"), { recursive: true });
  cpSync(join(root, "src/lib/topics.ts"), join(dir, "src/lib/topics.ts"));
  cpSync(join(root, "src/lib/content-schema.ts"), join(dir, "src/lib/content-schema.ts"));
  writeFileSync(join(dir, `src/content/${SLUG}.json`), JSON.stringify({ slug: SLUG, sections: [{ id: "s1" }, { id: "s2" }] }));
  const at = join(dir, "scripts/walkthroughs", file);
  mkdirSync(join(at, ".."), { recursive: true });
  writeFileSync(at, source);
  return dir;
}

const generated = (dir: string) => join(dir, `src/content/walkthroughs/${SLUG}/s1.json`);

test("the repo's walk-through files are what scripts/walkthroughs builds", { skip }, () => {
  const r = run(root, "--check");
  assert.equal(r.status, 0, r.output);
  assert.match(r.output, /\d+ walk-throughs?: the files are up to date/);
});

test("a build writes the JSON and the index, and then --check passes", { skip }, () => {
  const dir = fixture();
  try {
    const r = run(dir);
    assert.equal(r.status, 0, r.output);
    const walk = JSON.parse(readFileSync(generated(dir), "utf8"));
    assert.equal(walk.steps.length, 6);
    assert.equal(walk.steps[0].bn.short, "ধাপ ১", "Bangla digits in the Bangla text");
    assert.equal(readFileSync(generated(dir), "utf8"), JSON.stringify(walk, null, 2) + "\n", "2-space JSON with a trailing newline");
    const index = readFileSync(join(dir, "src/content/walkthroughs/index.ts"), "utf8");
    assert.match(index, /import llmFundamentalsS1 from "\.\/llm-fundamentals\/s1\.json";/);
    assert.match(index, /"llm-fundamentals": \{\n {4}s1: llmFundamentalsS1,\n {2}\},/);
    assert.equal(run(dir, "--check").status, 0);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("the check notices a hand edit, a missing file and a file with no source, and writes nothing", { skip }, () => {
  const dir = fixture();
  try {
    assert.equal(run(dir).status, 0);
    const edited = readFileSync(generated(dir), "utf8").replace("Title 1", "title 1");
    writeFileSync(generated(dir), edited);
    let r = run(dir, "--check");
    assert.equal(r.status, 1, r.output);
    assert.match(r.output, /DIFFERS src\/content\/walkthroughs\/llm-fundamentals\/s1\.json/);
    assert.doesNotMatch(r.output, /DIFFERS src\/content\/walkthroughs\/index\.ts/);
    assert.equal(readFileSync(generated(dir), "utf8"), edited, "--check must not write");

    rmSync(generated(dir));
    r = run(dir, "--check");
    assert.equal(r.status, 1, r.output);
    assert.match(r.output, /MISSING src\/content\/walkthroughs\/llm-fundamentals\/s1\.json/);
    assert.equal(existsSync(generated(dir)), false, "--check must not write");

    assert.equal(run(dir).status, 0);
    const stray = join(dir, `src/content/walkthroughs/${SLUG}/s2.json`);
    writeFileSync(stray, "{}\n");
    r = run(dir, "--check");
    assert.equal(r.status, 1, r.output);
    assert.match(r.output, /NO SOURCE src\/content\/walkthroughs\/llm-fundamentals\/s2\.json/);
    r = run(dir);
    assert.equal(r.status, 1, "a build refuses to run beside a file with no source, and deletes nothing");
    assert.equal(readFileSync(stray, "utf8"), "{}\n");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

// The builder is a script: importing it must not build, or a tool that wants one of its helpers rewrites the files.
test("importing build.py builds nothing: it runs only as a script", { skip }, () => {
  const dir = fixture();
  try {
    const code = [
      "import sys",
      `sys.argv = ["build.py", ${JSON.stringify(dir)}]`,
      `sys.path.insert(0, ${JSON.stringify(join(root, "scripts/walkthroughs"))})`,
      "import build",
      'print("imported")',
    ].join("\n");
    const r = spawnSync("python3", ["-c", code], { env, encoding: "utf8", timeout: 60_000 });
    assert.equal(r.status, 0, `${r.stdout}${r.stderr}`);
    assert.equal(r.stdout.trim(), "imported", "an import prints nothing of a build");
    assert.equal(existsSync(join(dir, "src/content/walkthroughs")), false, "an import writes nothing");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

// One planted defect at a time. Each must fail, say which rule, and name the step; and a failed build writes nothing.
const DEFECTS: { name: string; edit: (s: string) => string; message: RegExp }[] = [
  {
    name: "a Latin digit in Bangla text",
    edit: (s) => s.replace('"ধাপ {n} এর বিবরণ।"', '"ধাপ {i} এর বিবরণ।"'),
    message: /llm-fundamentals\/s1\.walkthrough\.step1\.bn\.body: Latin digits \['1'\]/,
  },
  {
    name: "a Bangla letter in English text",
    edit: (s) => s.replace('f"Body of step {i}."', 'f"Body of step {i} ক."'),
    message: /llm-fundamentals\/s1\.walkthrough\.step1\.en\.body: Bangla in English text/,
  },
  {
    name: "a label over 32 characters",
    edit: (s) => s.replace('("Server", "সার্ভার")', '("S" + "e" * 39, "সার্ভার")'),
    message: /llm-fundamentals\/s1\.walkthrough\.b\.en: .* is too long for any box \(40 chars, at most 32\)/,
  },
  {
    name: "a box on a line",
    edit: (s) =>
      s
        .replace('node("b", "server"', 'node("c", "cache", ("Cache", "ক্যাশ"), 290, 110), node("b", "server"')
        .replace("[step(i) for i in range(1, 7)]", '[step(i, extra_show=[sh("c")] if i == 3 else ()) for i in range(1, 7)]'),
    message: /llm-fundamentals\/s1\.walkthrough\.step3\.en: the line a → b runs through c/,
  },
  {
    name: "a kind the site does not draw",
    edit: (s) => s.replace('"user"', '"usr"'),
    message: /llm-fundamentals\/s1\.walkthrough: box 'a' has the unknown kind 'usr'/,
  },
  {
    name: "fewer than 6 steps",
    edit: (s) => s.replace("range(1, 7)", "range(1, 6)"),
    message: /llm-fundamentals\/s1\.walkthrough: 5 steps, a walk-through has 6 to 9/,
  },
  {
    name: "more than 8 boxes in one step",
    edit: () => boxes(9, 9),
    message: /llm-fundamentals\/s1\.walkthrough\.step1: 9 boxes shown, at most 8/,
  },
  {
    name: "more than 12 boxes in all",
    edit: () => boxes(13, 2),
    message: /llm-fundamentals\/s1\.walkthrough: 13 boxes in all, at most 12/,
  },
  {
    name: "a box 4px from the diagram's edge",
    edit: (s) => s.replace('"সার্ভার"), 460, 110)', '"সার্ভার"), 540, 110)'),
    message: /llm-fundamentals\/s1\.walkthrough\.step1\.en: b is 4px from the right edge, at least 10px/,
  },
  {
    name: "a box 12px under the top edge, where a badge needs 15px above the box",
    edit: (s) => s.replace('"সার্ভার"), 460, 110)', '"সার্ভার"), 460, 40)'),
    message: /llm-fundamentals\/s1\.walkthrough\.step1\.en: b is 12px from the top edge, at least 15px/,
  },
  {
    name: "two linked boxes 8px apart, so the arrow cannot be seen",
    edit: (s) => s.replace('"সার্ভার"), 460, 110)', '"সার্ভার"), 240, 110)').replace('ln("a", "b", "to", label=("asks", "চায়"))', 'ln("a", "b", "to")'),
    message: /llm-fundamentals\/s1\.walkthrough\.step1\.en: the line a → b shows only 8px, at least 20px/,
  },
  {
    name: "three paragraphs in a step",
    edit: (s) => s.replace('[(f"Body of step {i}.", body_bn.format(n=n, i=i))]', '[(f"A {i}.", "ক {n}.".format(n=n))] * 3'),
    message: /llm-fundamentals\/s1\.walkthrough\.step1: 3 paragraphs, at most 2/,
  },
];

for (const { name, edit, message } of DEFECTS) {
  test(`the build rejects ${name}, names the step, and writes nothing`, { skip }, () => {
    const dir = fixture(edit(SOURCE));
    try {
      const r = run(dir);
      assert.equal(r.status, 1, r.output);
      assert.match(r.output, message);
      assert.match(r.output, /nothing written/);
      assert.equal(existsSync(join(dir, "src/content/walkthroughs")), false, "a failed build writes nothing");
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
}

test("the build rejects a source for a section that does not exist, and one for a Part that does not exist", { skip }, () => {
  let dir = fixture(SOURCE, `${SLUG}/s9.py`);
  try {
    const r = run(dir);
    assert.equal(r.status, 1, r.output);
    assert.match(r.output, /llm-fundamentals\/s9: llm-fundamentals has no section "s9"/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
  dir = fixture(SOURCE, "no-such-part/s1.py");
  try {
    const r = run(dir);
    assert.equal(r.status, 1, r.output);
    assert.match(r.output, /no-such-part: not a Part/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
