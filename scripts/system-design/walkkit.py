"""Helpers for authoring walk-throughs. Every English text sits next to its Bangla text.

A walk-through is {width, height, nodes, metrics, caption, steps}. Build it with `walk(...)`:

    nodes   = [node(id, kind, (en, bn), x, y), ...]
    metrics = [(en, bn), ...]               # the labels of the readouts
    steps   = [st(short, title, body, show, links, values, note=, changes=, points=), ...]

`short`, `title`, each `body` paragraph, each `points` entry: (en, bn).
`note`: (kind, en, bn).  `changes`: [(sign, en, bn), ...].
`show`: [sh(id, state, sub=(en, bn), badge=, x=, y=), ...].  `links`: [ln(a, b, flow, ms, state, label=(en, bn)), ...].
`values`: one per metric: a plain string (digits turn Bangla on the Bangla site), a (en, bn) pair, or None for a dash.
"""


def bi(en, bn):
    return {"en": en, "bn": bn}


def node(id, kind, label, x, y):
    return {"id": id, "kind": kind, "label": bi(*label), "x": x, "y": y}


def sh(id, state=None, sub=None, badge=None, x=None, y=None):
    s = {"id": id}
    if state:
        s["state"] = state
    if sub:
        s["sub"] = bi(*sub)
    if badge:
        s["badge"] = badge
    if x is not None:
        s["x"] = x
    if y is not None:
        s["y"] = y
    return s


def ln(a, b, flow=None, ms=None, state=None, label=None):
    l = {"from": a, "to": b}
    if flow:
        l["flow"] = flow
    if ms:
        l["ms"] = ms
    if state:
        l["state"] = state
    if label:
        l["label"] = bi(*label)
    return l


def st(short, title, body, show, links=(), values=None, note=None, changes=None, points=None):
    """One step. Every text is an (en, bn) pair, so the two languages always have the same shape."""
    def side(i):
        t = {"short": short[i], "title": title[i], "body": [b[i] for b in body]}
        if note:
            t["note"] = {"kind": note[0], "html": note[1 + i]}
        if changes:
            t["changes"] = [{"sign": c[0], "html": c[1 + i]} for c in changes]
        if points:
            t["points"] = [p[i] for p in points]
        return t

    s = {"en": side(0), "bn": side(1), "show": list(show), "links": list(links)}
    if values is not None:
        s["values"] = [v if v is None or isinstance(v, str) else bi(*v) for v in values]
    return s


def walk(width, height, nodes, metrics, caption, steps):
    w = {"width": width, "height": height, "nodes": list(nodes), "metrics": [bi(*m) for m in metrics]}
    if caption:
        w["caption"] = bi(*caption)
    w["steps"] = list(steps)
    return w
