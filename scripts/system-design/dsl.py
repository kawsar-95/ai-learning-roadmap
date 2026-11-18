"""Tiny authoring helpers: each returns a block in the site's content schema."""


def p(html):
    return {"type": "paragraph", "html": html}


def h(html):
    """A level-3 heading. The builder gives it an id from the section id and its words."""
    return {"type": "heading", "level": 3, "html": html}


def ul(*items):
    return {"type": "list", "ordered": False, "items": list(items)}


def ol(*items):
    return {"type": "list", "ordered": True, "items": list(items)}


def table(headers, *rows):
    return {"type": "table", "headers": list(headers), "rows": [list(r) for r in rows]}


def note(variant, *paras):
    """A callout: info, good, warn, danger or pink."""
    return {"type": "callout", "variant": variant, "blocks": [p(x) for x in paras]}


def analogy(*paras):
    return {"type": "analogy", "blocks": [p(x) for x in paras]}


def code(lang, src):
    """The builder fills `html` with Shiki's github-dark-dimmed output."""
    return {"type": "code", "lang": lang, "code": src.strip("\n"), "html": None}


def S(lesson, title, sub, bn_title, bn_sub, body, layman, bangla):
    return {
        "lesson": lesson,
        "title": title,
        "sub": sub,
        "bn": {"title": bn_title, "sub": bn_sub},
        "body": body,
        "layman": layman,
        "bangla": bangla,
    }


def basics(idea, words, remember, bn_idea, bn_words, bn_remember):
    """A "Start here" box: the big idea, the words to know, and what to remember, in both languages."""
    def text(i, w, r):
        return {"idea": i, "words": [{"term": t, "meaning": m} for t, m in w], "remember": list(r)}
    return {"en": text(idea, words, remember), "bn": text(bn_idea, bn_words, bn_remember)}
