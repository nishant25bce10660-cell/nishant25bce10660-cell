#!/usr/bin/env python3
"""Render GitHub profile README cards as self-contained animated SVG images.

Usage:
    python scripts/generate_profile_cards.py
    STATIC=1 python scripts/generate_profile_cards.py

The script reads profile.json and data/contributions.json, then writes SVGs to
cards/. Font files are fetched from Google Fonts, subset with pyftsubset, and
embedded in each SVG as base64 WOFF data URIs. Existing local font files can be
provided through PROFILE_FONT_REGULAR and PROFILE_FONT_SEMIBOLD.
"""
from __future__ import annotations

import base64
import calendar
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "profile.json"
DATA_PATH = ROOT / "data" / "contributions.json"
CARDS_DIR = ROOT / "cards"
CACHE_DIR = ROOT / ".cache" / "profile-card-fonts"
STATIC = os.getenv("STATIC", "0").strip().lower() in {"1", "true", "yes"} or "--static" in sys.argv

DEFAULT_CONFIG: dict[str, Any] = {
    "username": "nishant25bce10660-cell",
    "name": "Nishant Singh",
    "tagline": "B.Tech CSE student at VIT Bhopal exploring web development and AI.",
    "location": "India",
    "website": "https://portos-azure.vercel.app/",
    "portrait": "",
    "theme": {
        "background": "#0B1018",
        "surface": "#111A27",
        "surface_alt": "#162235",
        "text": "#F4F7FC",
        "muted": "#9AAAC0",
        "border": "#26364B",
        "accent": "#0A84FF",
        "accent_light": "#62B5FF",
        "success": "#30D158",
    },
    "tiles": [
        {"eyebrow": "LIVE PROJECT", "title": "Portfolio OS", "detail": "Explore my desktop-style portfolio", "href": "https://portos-azure.vercel.app/", "glyph": "01"},
        {"eyebrow": "SOURCE CODE", "title": "GitHub", "detail": "Browse repositories and experiments", "href": "https://github.com/nishant25bce10660-cell", "glyph": "02"},
        {"eyebrow": "FEATURED WORK", "title": "PORT-OS", "detail": "A personal portfolio operating system", "href": "https://github.com/nishant25bce10660-cell/PORT-OS", "glyph": "03"},
    ],
    "repositories": [
        {"name": "PORT-OS", "description": "A macOS-inspired portfolio desktop with apps, windows, and a personal workspace.", "language": "JavaScript", "url": "https://github.com/nishant25bce10660-cell/PORT-OS", "label": "PORTFOLIO / WEB APP"},
        {"name": "SMS_SPAM_DETECTION", "description": "An NLP and machine-learning project that classifies SMS messages as spam or ham.", "language": "Python", "url": "https://github.com/nishant25bce10660-cell/SMS_SPAM_DETECTION", "label": "MACHINE LEARNING"},
        {"name": "digital-literacy-project", "description": "A digital-literacy project covering online safety, email etiquette, and awareness.", "language": "Documentation", "url": "https://github.com/nishant25bce10660-cell/digital-literacy-project", "label": "DIGITAL LITERACY"},
    ],
    "animation": {
        "hero": 0.10,
        "tiles": [0.85, 1.02, 1.19],
        "contributions": 1.60,
        "repositories": [2.35, 2.90, 3.45],
        "graph": 4.00,
    },
}

FONT_TEXT = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
    ".,:;!?@#$%&*()+-=_'\"/\\[]{}<>|~^`%"
    "áéíóúñüÁÉÍÓÚÑÜàèìòùç–—·•↗"
)


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read {path}: {exc}") from exc


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", value):
        raise ValueError(f"Expected a six-digit hex color, got {value!r}")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def mix_color(a: str, b: str, ratio: float) -> str:
    ar, ag, ab = hex_rgb(a)
    br, bg, bb = hex_rgb(b)
    values = [round(x + (y - x) * ratio) for x, y in ((ar, br), (ag, bg), (ab, bb))]
    return "#" + "".join(f"{v:02X}" for v in values)


def fetch_google_font(weight: int) -> Path:
    """Fetch the Latin Inter WOFF2 source; output is later subset to WOFF."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached = CACHE_DIR / f"inter-{weight}-latin.woff2"
    if cached.exists() and cached.stat().st_size > 5000:
        return cached

    css_url = f"https://fonts.googleapis.com/css2?family=Inter:wght@{weight}&display=swap"
    request = urllib.request.Request(
        css_url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        css = response.read().decode("utf-8")

    blocks = re.findall(r"@font-face\s*\{([^}]+)\}", css, flags=re.I | re.S)
    latin_url = None
    for block in blocks:
        if "font-style: normal" not in block.replace("\n", " "):
            continue
        src_match = re.search(r"src:\s*url\((https://[^)]+)\)\s*format\(['\"]woff2['\"]\)", block)
        if src_match and "U+0000-00FF" in block:
            latin_url = src_match.group(1)
            break
    if not latin_url:
        # Some Google CSS revisions omit explicit unicode-range. Prefer a WOFF2 source.
        for block in blocks:
            src_match = re.search(r"src:\s*url\((https://[^)]+)\)\s*format\(['\"]woff2['\"]\)", block)
            if src_match:
                latin_url = src_match.group(1)
                break
    if not latin_url:
        raise RuntimeError(f"Could not find an Inter WOFF2 font URL for weight {weight}.")

    with urllib.request.urlopen(latin_url, timeout=30) as response:
        cached.write_bytes(response.read())
    return cached


def subset_font(weight: int, text_chars: str) -> str:
    """Return a base64-encoded WOFF subset for an Inter face."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    env_key = "PROFILE_FONT_REGULAR" if weight == 400 else "PROFILE_FONT_SEMIBOLD"
    local = os.getenv(env_key)
    if local and Path(local).expanduser().is_file():
        source = Path(local).expanduser().resolve()
    else:
        local_name = "Inter-Regular.ttf" if weight == 400 else "Inter-SemiBold.ttf"
        candidates = [ROOT / "assets" / "fonts" / local_name]
        source = next((p for p in candidates if p.is_file()), None)  # type: ignore[assignment]
        if source is None:
            source = fetch_google_font(weight)

    digest = hashlib.sha256((str(source) + text_chars + str(weight)).encode("utf-8")).hexdigest()[:16]
    output = CACHE_DIR / f"inter-{weight}-{digest}.woff"
    if not output.exists():
        pyftsubset = shutil.which("pyftsubset")
        if not pyftsubset:
            raise RuntimeError("pyftsubset was not found. Install it with: pip install 'fonttools[woff]'")
        command = [
            pyftsubset,
            str(source),
            f"--output-file={output}",
            "--flavor=woff",
            f"--text={text_chars}",
            "--layout-features=*",
            "--glyph-names",
            "--symbol-cmap",
            "--legacy-cmap",
            "--notdef-glyph",
            "--notdef-outline",
            "--recommended-glyphs",
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
    return base64.b64encode(output.read_bytes()).decode("ascii")


def font_css(config: dict[str, Any]) -> str:
    regular = subset_font(400, FONT_TEXT)
    semibold = subset_font(600, FONT_TEXT)
    return (
        "@font-face{font-family:'ProfileInter';font-style:normal;font-weight:400;"
        f"src:url(data:font/woff;base64,{regular}) format('woff');}}"
        "@font-face{font-family:'ProfileInter';font-style:normal;font-weight:600;"
        f"src:url(data:font/woff;base64,{semibold}) format('woff');}}"
    )


def animation_css(static: bool) -> str:
    base = """
      text{font-family:'ProfileInter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
      .mono{font-family:ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace;letter-spacing:.04em}
      .muted{fill:var(--muted)}
    """
    if static:
        return base
    return base + """
      @keyframes card-enter{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
      @keyframes soft-glow{0%,100%{opacity:.58}50%{opacity:1}}
      @keyframes tile-line{from{stroke-dashoffset:170}to{stroke-dashoffset:0}}
      .reveal{animation:card-enter .72s cubic-bezier(.2,.72,.2,1) var(--delay,0s) both}
      .glow{animation:soft-glow 3.2s ease-in-out 1.2s infinite}
      .draw-line{stroke-dasharray:170;animation:tile-line .8s ease-out 1.1s both}
      @media(prefers-reduced-motion:reduce){
        .reveal,.glow,.draw-line{animation:none!important;opacity:1!important;transform:none!important;stroke-dashoffset:0!important}
        animate,set{display:none!important}
      }
    """


def shell(title: str, width: int, height: int, theme: dict[str, str], fonts: str, body: str, defs: str = "", static: bool = False) -> str:
    css = fonts + animation_css(static)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style><![CDATA[
:root{{--bg:{theme['background']};--surface:{theme['surface']};--surface-alt:{theme['surface_alt']};--text:{theme['text']};--muted:{theme['muted']};--border:{theme['border']};--accent:{theme['accent']};--accent-light:{theme['accent_light']};}}
{css}
]]></style>
<defs>{defs}</defs>
{body}
</svg>'''


def bg_rect(width: int, height: int, theme: dict[str, str], radius: int = 28) -> str:
    return f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="{radius}" fill="{theme["surface"]}" stroke="{theme["border"]}" stroke-width="2"/>'


def text_node(x: float, y: float, value: str, size: int, fill: str, weight: int = 400, extra: str = "") -> str:
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" {extra}>{esc(value)}</text>'


def reveal_class(delay: float, static: bool) -> str:
    return "" if static else f'class="reveal" style="--delay:{max(0.0, delay):.2f}s"'



def load_contribution_days(raw: dict[str, Any]) -> dict[date, int]:
    """Accept either GitHub GraphQL output or a normalized {days:[...]} file."""
    rows: list[dict[str, Any]] = []
    if isinstance(raw.get("days"), list):
        rows = raw["days"]
    else:
        try:
            weeks = raw["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            for week in weeks:
                rows.extend(week.get("contributionDays", []))
        except (KeyError, TypeError):
            # Empty initial file is valid until the first scheduled Action run.
            rows = []
    result: dict[date, int] = {}
    for row in rows:
        try:
            day = date.fromisoformat(str(row["date"])[:10])
            count = int(row.get("contributionCount", row.get("count", 0)))
            result[day] = max(0, count)
        except (KeyError, TypeError, ValueError):
            continue
    return result


def contribution_metrics(days: dict[date, int], today: date) -> dict[str, Any]:
    start = today - timedelta(days=364)
    values = {start + timedelta(days=i): days.get(start + timedelta(days=i), 0) for i in range(365)}
    # The 53-column calendar needs up to six padding days before the 365-day window.
    heatmap_values = {today - timedelta(days=370) + timedelta(days=i): days.get(today - timedelta(days=370) + timedelta(days=i), 0) for i in range(371)}
    active_days = sum(1 for count in values.values() if count > 0)
    total = sum(values.values())

    longest = current = run = 0
    for day in sorted(values):
        if values[day] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    cursor = today if values.get(today, 0) > 0 else today - timedelta(days=1)
    while cursor >= start and values.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    weekday_totals = [0] * 7
    for day, count in values.items():
        weekday_totals[day.weekday()] += count
    best_index = max(range(7), key=lambda idx: weekday_totals[idx]) if total else None
    best_weekday = calendar.day_name[best_index][:3] if best_index is not None else "—"
    best_weekday_total = weekday_totals[best_index] if best_index is not None else 0

    month_labels: list[str] = []
    monthly: list[int] = []
    first_month = date(today.year, today.month, 1)
    for offset in range(11, -1, -1):
        year = first_month.year
        month = first_month.month - offset
        while month <= 0:
            year -= 1
            month += 12
        month_start = date(year, month, 1)
        month_end = date(year + (month == 12), 1 if month == 12 else month + 1, 1)
        month_labels.append(calendar.month_abbr[month_start.month])
        monthly.append(sum(count for day, count in values.items() if month_start <= day < month_end))

    latest_peak = max(values.items(), key=lambda item: item[1]) if total else None
    return {
        "active_days": active_days,
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_weekday": best_weekday,
        "best_weekday_total": best_weekday_total,
        "month_labels": month_labels,
        "monthly": monthly,
        "peak_date": latest_peak[0].isoformat() if latest_peak else "—",
        "peak_count": latest_peak[1] if latest_peak else 0,
        "values": values,
        "heatmap_values": heatmap_values,
    }


def make_hero(config: dict[str, Any], theme: dict[str, str], fonts: str, static: bool) -> str:
    delay = float(config["animation"].get("hero", 0.1))
    name = config["name"]
    tagline = config["tagline"]
    tagline_lines = textwrap.wrap(tagline, width=68)[:2]
    defs = '''<linearGradient id="hero-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#17263B"/><stop offset="1" stop-color="#0D1521"/></linearGradient>
<radialGradient id="hero-orb"><stop offset="0" stop-color="{accent}" stop-opacity=".36"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>'''.format(accent=theme['accent'])
    parts = [
        '<rect x="1" y="1" width="1198" height="358" rx="30" fill="url(#hero-grad)" stroke="' + theme['border'] + '" stroke-width="2"/>',
        '<circle cx="1040" cy="90" r="250" fill="url(#hero-orb)" class="glow"/>',
        f'<g {reveal_class(delay, static)}>',
        text_node(58, 68, "NISHANT / PROFILE", 16, theme['accent_light'], 600, 'class="mono"'),
        '<circle cx="63" cy="108" r="5" fill="' + theme['success'] + '"/>',
        text_node(80, 114, "OPEN TO LEARNING & BUILDING", 14, theme['muted'], 600, 'class="mono"'),
        text_node(58, 208, name, 66, theme['text'], 600, 'letter-spacing="-2.6"'),
    ]
    for i, line in enumerate(tagline_lines):
        parts.append(text_node(62, 258 + i * 31, line, 21, theme['muted'], 400))
    parts += [
        text_node(62, 328, f"{config.get('location', 'India')}  /  WEB DEVELOPMENT  /  SOFTWARE EXPERIMENTS", 13, theme['accent_light'], 600, 'class="mono"'),
        '</g>',
    ]

    portrait = str(config.get("portrait", "")).strip()
    portrait_path = (ROOT / portrait).resolve() if portrait else None
    if portrait_path and portrait_path.is_file() and ROOT in portrait_path.parents:
        mime = "image/png" if portrait_path.suffix.lower() == ".png" else "image/jpeg"
        encoded = base64.b64encode(portrait_path.read_bytes()).decode("ascii")
        parts.append('<circle cx="1036" cy="181" r="124" fill="none" stroke="' + theme['accent'] + '" stroke-opacity=".32" stroke-width="2"/>')
        parts.append('<clipPath id="portrait-clip"><circle cx="1036" cy="181" r="105"/></clipPath>')
        parts.append(f'<image x="931" y="76" width="210" height="210" preserveAspectRatio="xMidYMid slice" clip-path="url(#portrait-clip)" href="data:{mime};base64,{encoded}"/>')
    else:
        parts.append(f'<circle cx="1036" cy="181" r="118" fill="{theme["surface_alt"]}" stroke="{theme["border"]}" stroke-width="2"/>')
        parts.append(f'<circle cx="1036" cy="181" r="101" fill="none" stroke="{theme["accent"]}" stroke-width="2" stroke-opacity=".55"/>')
        parts.append(text_node(1036, 203, "NS", 72, theme['text'], 600, 'text-anchor="middle" letter-spacing="-4"'))
        parts.append(text_node(1036, 330, "BUILD / LEARN / REPEAT", 12, theme['muted'], 600, 'text-anchor="middle" class="mono"'))
    return shell("Nishant Singh - GitHub profile", 1200, 360, theme, fonts, "".join(parts), defs, static)


def make_tile(tile: dict[str, Any], index: int, delay: float, theme: dict[str, str], fonts: str, static: bool) -> str:
    defs = f'''<linearGradient id="tile{index}-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{theme['surface_alt']}"/><stop offset="1" stop-color="{theme['surface']}"/></linearGradient>'''
    body = [
        f'<rect x="1" y="1" width="1198" height="278" rx="25" fill="url(#tile{index}-grad)" stroke="{theme["border"]}" stroke-width="2"/>',
        f'<g {reveal_class(delay, static)}>',
        text_node(42, 55, str(tile.get("eyebrow", "LINK")), 14, theme['accent_light'], 600, 'class="mono"'),
        text_node(42, 126, str(tile.get("title", f"Link {index}")), 38, theme['text'], 600),
        text_node(42, 170, str(tile.get("detail", "Open link")), 18, theme['muted'], 400),
        text_node(43, 239, f"OPEN / {str(tile.get('glyph', f'{index:02d}'))}", 13, theme['accent_light'], 600, 'class="mono"'),
        f'<path d="M930 225 L1090 65" stroke="{theme["accent"]}" stroke-width="2" stroke-linecap="round" class="draw-line"/>',
        f'<path d="M1038 65 H1090 V117" fill="none" stroke="{theme["accent_light"]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<circle cx="1080" cy="202" r="42" fill="{theme["accent"]}" fill-opacity=".10"/>',
        text_node(1080, 211, str(tile.get("glyph", f"{index:02d}")), 22, theme['accent_light'], 600, 'text-anchor="middle" class="mono"'),
        '</g>',
    ]
    return shell(str(tile.get("title", "Profile link")), 1200, 280, theme, fonts, "".join(body), defs, static)


def make_contributions(metrics: dict[str, Any], theme: dict[str, str], fonts: str, delay: float, static: bool) -> str:
    width, height = 1200, 430
    body = [bg_rect(width, height, theme, 28), f'<g {reveal_class(delay, static)}>']
    body += [
        text_node(56, 62, "CONTRIBUTION ACTIVITY", 15, theme['accent_light'], 600, 'class="mono"'),
        text_node(56, 105, "A year of contributions and momentum", 30, theme['text'], 600),
        text_node(1140, 64, "LAST 12 MONTHS", 13, theme['muted'], 600, 'text-anchor="end" class="mono"'),
    ]
    if metrics["total"] == 0:
        body.append(text_node(1140, 105, "AWAITING FIRST DAILY SYNC", 12, theme['muted'], 500, 'text-anchor="end" class="mono"'))

    # Metric strip
    stat_y = 154
    stats = [
        ("TOTAL CONTRIBUTIONS", f"{metrics['total']:,}"),
        ("CURRENT STREAK", f"{metrics['current_streak']} days"),
        ("LONGEST STREAK", f"{metrics['longest_streak']} days"),
        ("ACTIVE DAYS", f"{metrics['active_days']}"),
        ("BUSIEST WEEKDAY", f"{metrics['best_weekday']}  /  {metrics['best_weekday_total']:,}"),
    ]
    stat_xs = [58, 280, 505, 730, 940]
    for x, (label, value) in zip(stat_xs, stats):
        body.append(text_node(x, stat_y, label, 11, theme['muted'], 600, 'class="mono"'))
        body.append(text_node(x, stat_y + 40, value, 25, theme['text'], 600))
    body.append(f'<path d="M56 218 H1144" stroke="{theme["border"]}" stroke-width="1"/>')

    plot_top, baseline = 254, 356
    max_value = max(metrics["monthly"]) if metrics["monthly"] else 0
    max_value = max(1, max_value)
    x0, bar_w, step = 86, 46, 87
    for i, (label, value) in enumerate(zip(metrics["month_labels"], metrics["monthly"])):
        bar_h = max(2, (value / max_value) * (baseline - plot_top)) if value else 2
        x = x0 + i * step
        y = baseline - bar_h
        animation = ""
        if not static:
            animation = (
                f'<animate attributeName="height" from="0" to="{bar_h:.1f}" begin="{delay + 0.28 + i * 0.055:.2f}s" dur=".72s" fill="freeze"/>'
                f'<animate attributeName="y" from="{baseline}" to="{y:.1f}" begin="{delay + 0.28 + i * 0.055:.2f}s" dur=".72s" fill="freeze"/>'
            )
        body.append(f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{bar_h:.1f}" rx="8" fill="{mix_color(theme["surface_alt"], theme["accent"], 0.88)}" fill-opacity=".94">{animation}</rect>')
        body.append(text_node(x + bar_w / 2, 385, label, 13, theme['muted'], 500, 'text-anchor="middle" class="mono"'))
        if value > 0 and (value == max(metrics["monthly"]) or i in (0, 5, 11)):
            body.append(text_node(x + bar_w / 2, max(plot_top - 8, y - 10), str(value), 11, theme['accent_light'], 600, 'text-anchor="middle" class="mono"'))
    body.append(text_node(58, 410, f"PEAK DAY  {metrics['peak_date']}  /  {metrics['peak_count']} contributions", 11, theme['muted'], 500, 'class="mono"'))
    body.append('</g>')
    return shell("GitHub contribution activity, streak and monthly chart", width, height, theme, fonts, "".join(body), static=static)


def make_repo(repo: dict[str, Any], index: int, delay: float, theme: dict[str, str], fonts: str, static: bool) -> str:
    width, height = 1200, 230
    body = [bg_rect(width, height, theme, 26), f'<g {reveal_class(delay, static)}>']
    body += [
        text_node(52, 49, f"FEATURED REPOSITORY  /  {index:02d}", 13, theme['accent_light'], 600, 'class="mono"'),
        text_node(52, 108, str(repo.get("name", "Repository")), 35, theme['text'], 600),
    ]
    description = textwrap.wrap(str(repo.get("description", "")), width=105)[:2]
    for line_idx, line in enumerate(description):
        body.append(text_node(54, 151 + line_idx * 25, line, 17, theme['muted'], 400))
    body += [
        f'<rect x="920" y="54" width="225" height="44" rx="22" fill="{theme["accent"]}" fill-opacity=".13" stroke="{theme["accent"]}" stroke-opacity=".35"/>',
        text_node(1032, 82, str(repo.get("language", repo.get("label", "PROJECT"))).upper(), 13, theme['accent_light'], 600, 'text-anchor="middle" class="mono"'),
        text_node(1140, 177, "VIEW SOURCE  /  ↗", 13, theme['accent_light'], 600, 'text-anchor="end" class="mono"'),
        '</g>',
    ]
    return shell(f"Featured repository {repo.get('name', '')}", width, height, theme, fonts, "".join(body), static=static)


def make_heatmap(metrics: dict[str, Any], theme: dict[str, str], fonts: str, delay: float, static: bool) -> str:
    width, height = 1200, 260
    body = [bg_rect(width, height, theme, 28), f'<g {reveal_class(delay, static)}>']
    body += [
        text_node(54, 52, "CONTRIBUTION GRAPH", 15, theme['accent_light'], 600, 'class="mono"'),
        text_node(54, 90, "Consistency, one day at a time", 27, theme['text'], 600),
    ]
    # GitHub-like 53 x 7 calendar, Sunday first.
    today = date.today()
    start = today - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    cell, gap, x0, y0 = 13, 5, 78, 119
    weekday_labels = [("Mon", 1), ("Wed", 3), ("Fri", 5)]
    for label, row in weekday_labels:
        body.append(text_node(47, y0 + row * (cell + gap) + 11, label, 10, theme['muted'], 500, 'text-anchor="end" class="mono"'))
    month_seen: set[tuple[int, int]] = set()
    accent = theme['accent']
    zero = mix_color(theme['surface'], theme['surface_alt'], 0.75)
    for week in range(53):
        for weekday in range(7):
            day = start + timedelta(days=week * 7 + weekday)
            if day > today:
                continue
            count = metrics['heatmap_values'].get(day, 0)
            if count <= 0:
                fill = zero
            else:
                # Saturation steps remain within the accent hue.
                ratio = 0.22 if count == 1 else 0.42 if count <= 3 else 0.66 if count <= 6 else 0.96
                fill = mix_color(theme['surface_alt'], accent, ratio)
            x = x0 + week * (cell + gap)
            y = y0 + weekday * (cell + gap)
            animation = ""
            if not static and count > 0:
                animation = f'<animate attributeName="opacity" from="0" to="1" begin="{delay + 0.08 + week * 0.018 + weekday * 0.004:.2f}s" dur=".32s" fill="freeze"/>'
            body.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{fill}">{animation}</rect>')
            if day.day == 1:
                key = (day.year, day.month)
                if key not in month_seen:
                    month_seen.add(key)
                    body.append(text_node(x, 109, calendar.month_abbr[day.month], 10, theme['muted'], 500, 'class="mono"'))
    legend_y = 239
    body.append(text_node(930, legend_y, "LESS", 10, theme['muted'], 500, 'class="mono"'))
    for i in range(5):
        fill = zero if i == 0 else mix_color(theme['surface_alt'], accent, [0, .22, .42, .66, .96][i])
        body.append(f'<rect x="{970 + i * 17}" y="{legend_y - 11}" width="12" height="12" rx="3" fill="{fill}"/>')
    body.append(text_node(1063, legend_y, "MORE", 10, theme['muted'], 500, 'class="mono"'))
    body.append('</g>')
    return shell("GitHub contribution graph in profile brand color", width, height, theme, fonts, "".join(body), static=static)


def write_cards(config: dict[str, Any], raw_data: dict[str, Any]) -> list[Path]:
    theme = config["theme"]
    theme.setdefault("surface_alt", theme["surface"])
    theme.setdefault("accent_light", theme["accent"])
    fonts = font_css(config)
    days = load_contribution_days(raw_data)
    metrics = contribution_metrics(days, date.today())
    CARDS_DIR.mkdir(parents=True, exist_ok=True)

    output: list[Path] = []
    hero_path = CARDS_DIR / "hero.svg"
    hero_path.write_text(make_hero(config, theme, fonts, STATIC), encoding="utf-8")
    output.append(hero_path)

    tiles = list(config.get("tiles", []))[:3]
    if len(tiles) != 3:
        raise ValueError("profile.json must define exactly three tiles.")
    tile_delays = config["animation"].get("tiles", [0.85, 1.02, 1.19])
    for index, tile in enumerate(tiles, start=1):
        path = CARDS_DIR / f"tile-{index}.svg"
        path.write_text(make_tile(tile, index, float(tile_delays[index - 1]), theme, fonts, STATIC), encoding="utf-8")
        output.append(path)

    contribution_path = CARDS_DIR / "contributions.svg"
    contribution_path.write_text(
        make_contributions(metrics, theme, fonts, float(config["animation"].get("contributions", 1.6)), STATIC),
        encoding="utf-8",
    )
    output.append(contribution_path)

    repos = list(config.get("repositories", []))
    repo_delays = config["animation"].get("repositories", [])
    for index, repo in enumerate(repos, start=1):
        delay = float(repo_delays[index - 1]) if index - 1 < len(repo_delays) else 2.2 + index * 0.45
        slug = re.sub(r"[^a-z0-9]+", "-", str(repo.get("name", f"repo-{index}")).lower()).strip("-")
        path = CARDS_DIR / f"repo-{slug}.svg"
        path.write_text(make_repo(repo, index, delay, theme, fonts, STATIC), encoding="utf-8")
        output.append(path)

    graph_path = CARDS_DIR / "contribution-graph.svg"
    graph_path.write_text(make_heatmap(metrics, theme, fonts, float(config["animation"].get("graph", 4.0)), STATIC), encoding="utf-8")
    output.append(graph_path)

    # Machine-readable metrics make it easy to validate the daily refresh.
    metrics_path = CARDS_DIR / "metrics.json"
    metrics_export = {k: v for k, v in metrics.items() if k not in {"values", "heatmap_values"}}
    metrics_path.write_text(json.dumps(metrics_export, indent=2) + "\n", encoding="utf-8")
    output.append(metrics_path)
    return output


def main() -> int:
    config = deep_merge(DEFAULT_CONFIG, read_json(CONFIG_PATH, {}))
    raw_data = read_json(DATA_PATH, {"days": []})
    try:
        files = write_cards(config, raw_data)
    except Exception as exc:  # Give Actions a useful error instead of a silent partial build.
        print(f"Card generation failed: {exc}", file=sys.stderr)
        return 1
    mode = "static final-frame" if STATIC else "animated"
    print(f"Generated {len(files)} files in {CARDS_DIR.relative_to(ROOT)}/ ({mode} mode):")
    for path in files:
        print(f"  - {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
