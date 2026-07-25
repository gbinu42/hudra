#!/usr/bin/env python3
"""Convert Quill Delta JSON (as used by hudra.org) to plain text or HTML."""

from __future__ import annotations

import html
import json
import re
from typing import Any


# Canonical liturgical red for all rubrics in HTML output.
RUBRIC_COLOR = "#ee0000"

# Red family (already rubrics in source).
RED_RUBRIC_COLORS = {
    "#ee0000",
    "#ff0000",
    "#c00000",
    "#dc143c",
    "#e60000",
    "red",
}

# Non-red Word/Quill theme colors used as rubrics (esp. Assyrian texts).
ALT_RUBRIC_COLORS = {
    "#2e74b5",
    "#2e75b6",
    "#0f4761",
    "#104862",
    "#5b9bd5",
    "#4f81bd",
    "#365f91",
    "#376092",
    "#215e99",
    "#0070c0",
    "#00b0f0",
    "#004e9a",
    "#004f88",
    "#0066cc",
    "#0563c1",
    "#467886",
    "#31849b",
    "blue",
}

RUBRIC_COLORS = RED_RUBRIC_COLORS | ALT_RUBRIC_COLORS

# Named CSS colors Quill sometimes emits — keep them valid for inline style.
COLOR_ALIASES = {
    "red": RUBRIC_COLOR,
    "blue": RUBRIC_COLOR,
    "black": "#14261c",
}


def _unwrap(value: Any) -> Any:
    """Unwrap double-encoded JSON strings from the API."""
    while isinstance(value, str):
        s = value.strip()
        if not s:
            return ""
        if s[0] in "{[\"":
            try:
                value = json.loads(s)
                continue
            except json.JSONDecodeError:
                return value
        return value
    return value


def _normalize_color(color: str | None) -> str | None:
    if not color:
        return None
    c = str(color).strip()
    if not c:
        return None
    low = c.lower()
    if low in COLOR_ALIASES:
        return COLOR_ALIASES[low]
    if re.fullmatch(r"#[0-9a-fA-F]{3,8}", c):
        # Prefer lowercase hex; keep 7-char form as-is casing from source then lower.
        return low if len(c) == 7 else c.lower()
    if re.fullmatch(r"#[0-9a-fA-F]{3,8}", low):
        return low
    # Allow simple named colors through unchanged
    if re.fullmatch(r"[a-zA-Z]+", c):
        return low
    return None


def _is_rubric_color(color: str | None) -> bool:
    if not color:
        return False
    c = color.lower().strip()
    return c in RUBRIC_COLORS


def _display_color(color: str | None) -> str | None:
    """Map rubric colors (red or alt) to canonical red; leave body ink alone."""
    normalized = _normalize_color(color)
    if not normalized:
        return None
    if _is_rubric_color(normalized) or _is_rubric_color(str(color).lower().strip()):
        return RUBRIC_COLOR
    return normalized


def _is_rubric(attrs: dict | None) -> bool:
    if not attrs:
        return False
    color = str(attrs.get("color", "")).lower().strip()
    if _is_rubric_color(color):
        return True
    if attrs.get("bold") and color.startswith("#e"):
        return True
    return False


def _ops(raw: Any) -> list[dict]:
    data = _unwrap(raw)
    if isinstance(data, dict) and isinstance(data.get("ops"), list):
        return [o for o in data["ops"] if isinstance(o, dict)]
    return []


def quill_to_html(raw: Any) -> str:
    """
    Convert Quill Delta to HTML, preserving colors, bold/italic, and alignment.
    Output is a sequence of <p> blocks with optional inline <span>/<strong>/<em>.
    """
    ops = _ops(raw)
    if not ops:
        text = _unwrap(raw)
        if isinstance(text, str) and text.strip():
            paras = [f"<p>{html.escape(p)}</p>" for p in text.splitlines() if p.strip()]
            return "\n".join(paras)
        return ""

    # Build paragraphs: each ends at a newline; align attrs live on the newline.
    paragraphs: list[tuple[str | None, list[tuple[str, dict]]]] = []
    current: list[tuple[str, dict]] = []
    pending_align: str | None = None

    def flush(align: str | None) -> None:
        nonlocal current
        # Keep empty paragraphs that are intentional blank lines? Skip empties.
        if not current:
            return
        paragraphs.append((align, current))
        current = []

    for op in ops:
        insert = op.get("insert")
        attrs = op.get("attributes") if isinstance(op.get("attributes"), dict) else {}
        if not isinstance(insert, str):
            continue
        parts = insert.split("\n")
        for i, part in enumerate(parts):
            if part:
                current.append((part, attrs))
            if i < len(parts) - 1:
                # Newline: alignment comes from this op's attributes
                align = attrs.get("align") if isinstance(attrs.get("align"), str) else pending_align
                flush(align)
                pending_align = None

    flush(None)

    out: list[str] = []
    for align, runs in paragraphs:
        pieces: list[str] = []
        for text, attrs in runs:
            escaped = html.escape(text)
            color = _display_color(attrs.get("color") if isinstance(attrs, dict) else None)
            styles: list[str] = []
            if color:
                styles.append(f"color:{color}")
            size = attrs.get("size") if isinstance(attrs, dict) else None
            if isinstance(size, str) and size:
                styles.append(f"font-size:{html.escape(size)}")
            inner = escaped
            if attrs.get("bold"):
                inner = f"<strong>{inner}</strong>"
            if attrs.get("italic"):
                inner = f"<em>{inner}</em>"
            if attrs.get("underline"):
                inner = f"<u>{inner}</u>"
            if styles:
                inner = f'<span style="{";".join(styles)}">{inner}</span>'
            pieces.append(inner)
        body = "".join(pieces).strip()
        if not body:
            continue
        align_attr = f' class="align-{html.escape(align)}"' if align in ("center", "right", "left", "justify") else ""
        out.append(f"<p{align_attr}>{body}</p>")

    return "\n".join(out)


def quill_to_text(raw: Any) -> str:
    """
    Convert a Quill Delta (or API-wrapped string) to readable Syriac text.

    Rubrics / titles (typically red) are wrapped with blank lines for clarity.
    Alignment and other rich-text attributes are ignored; line breaks are kept.
    """
    data = _unwrap(raw)
    if data is None:
        return ""
    if isinstance(data, str):
        return data.strip() + ("\n" if data.strip() else "")

    ops = data.get("ops") if isinstance(data, dict) else None
    if not isinstance(ops, list):
        return str(data).strip() + "\n"

    lines: list[str] = []
    buf: list[str] = []
    pending_blank = False

    def flush(as_rubric: bool = False) -> None:
        nonlocal pending_blank
        text = "".join(buf).rstrip()
        buf.clear()
        if not text:
            return
        if as_rubric:
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(text)
            pending_blank = True
        else:
            if pending_blank:
                lines.append("")
                pending_blank = False
            lines.append(text)

    current_rubric = False
    for op in ops:
        if not isinstance(op, dict):
            continue
        insert = op.get("insert")
        attrs = op.get("attributes") if isinstance(op.get("attributes"), dict) else {}

        if not isinstance(insert, str):
            # Embeds / images — skip
            continue

        rubric = _is_rubric(attrs)
        parts = insert.split("\n")
        for i, part in enumerate(parts):
            if i > 0:
                flush(as_rubric=current_rubric)
                current_rubric = rubric
            if part:
                if buf and current_rubric != rubric:
                    flush(as_rubric=current_rubric)
                    current_rubric = rubric
                elif not buf:
                    current_rubric = rubric
                buf.append(part)

    flush(as_rubric=current_rubric)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


if __name__ == "__main__":
    import sys

    raw = sys.stdin.read()
    sys.stdout.write(quill_to_text(raw))
