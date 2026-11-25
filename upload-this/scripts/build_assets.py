#!/usr/bin/env python3
"""
Rebuilds every animated asset in /assets and the README.md.
Edit the CONFIG block below, then run:   python scripts/build_assets.py
(Needs Python 3 + Pillow for the GIF:  pip install pillow)
"""
import html, math, pathlib, random

# ───────────────────────── CONFIG (edit me) ─────────────────────────
CFG = dict(
    user="nishant25bce10660-cell",
    name="Nishant Singh",
    initials="NS",
    roles=["B.Tech CSE Student", "Web Developer", "Machine Learning Explorer", "Building PORT-OS"],
    portfolio="https://portos-azure.vercel.app/",
    terminal=[  # ("cmd", text) is typed, ("out", text) fades in
        ("cmd", "whoami"), ("out", "Nishant Singh · B.Tech CSE"),
        ("cmd", "cat focus.txt"), ("out", "web dev · machine learning · open source"),
        ("cmd", "ls projects/"), ("out", "PORT-OS  SMS_SPAM_DETECTION  digital-literacy"),
        ("cmd", "echo $STATUS"), ("out", "open to collaborate"),
    ],
    orbit=[  # three rings: inner, middle, outer
        ["Python", "JavaScript", "Git"],
        ["HTML5", "CSS3", "Linux", "GitHub"],
        ["Machine Learning", "Data Structures", "Pandas", "NumPy", "Open Source"],
    ],
    marquee=[
        ["Python", "JavaScript", "HTML5", "CSS3", "Git", "GitHub", "Linux", "VS Code"],
        ["Machine Learning", "Data Structures", "Algorithms", "Scikit-learn", "Pandas", "NumPy", "Responsive UI", "Open Source"],
    ],
    projects=[  # title, description lines, tags, link
        ("PORT-OS", ["A portfolio that behaves like", "a tiny operating system."], ["Web", "UI", "Portfolio"],
         "https://github.com/nishant25bce10660-cell/PORT-OS"),
        ("SMS Spam Detection", ["Machine-learning model that", "flags spam text messages."], ["Python", "ML", "NLP"],
         "https://github.com/nishant25bce10660-cell/SMS_SPAM_DETECTION"),
        ("Digital Literacy Project", ["Making everyday digital skills", "simple to learn and use."], ["Education", "Web"],
         "https://github.com/nishant25bce10660-cell/digital-literacy-project"),
    ],
    learning=[("Machine Learning", 65), ("Web Development", 80), ("Data Structures & Algorithms", 60), ("Open Source", 45)],
)
# ────────────────────────────────────────────────────────────────────

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

BG, BG2, PANEL, LINE = "#0b1020", "#171236", "#0f1630", "#222c55"
CY, VI, PK, GR, YE = "#22d3ee", "#8b5cf6", "#f472b6", "#34d399", "#fbbf24"
TXT, MUT = "#e6edf7", "#8b9ab8"
PAL = [CY, VI, PK, GR, YE]
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "Consolas, 'Courier New', Menlo, monospace"
esc = lambda s: html.escape(s, quote=True)


def save(name, svg):
    (OUT / name).write_text(svg, encoding="utf-8")


def grad(id_, w=1200):
    """Animated flowing gradient (cyan→violet→pink, reflected)."""
    return (f'<linearGradient id="{id_}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w//2}" y2="0" spreadMethod="reflect">'
            f'<stop offset="0" stop-color="{CY}"/><stop offset=".5" stop-color="{VI}"/><stop offset="1" stop-color="{PK}"/>'
            f'<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{w} 0" dur="7s" repeatCount="indefinite"/>'
            f'</linearGradient>')


def wave(base, amp, period, phase, w=2400, bottom=400):
    pts = [f"{x},{base + amp * math.sin(2 * math.pi * x / period + phase):.1f}" for x in range(0, w + 1, 20)]
    return "M" + " L".join(pts) + f" L{w},{bottom} L0,{bottom} Z"


# ───────────────────────── 1. HEADER ─────────────────────────
def header():
    W, H = 1200, 340
    r = random.Random(7)
    stars = "".join(
        f'<circle class="tw" cx="{r.randint(10, W-10)}" cy="{r.randint(8, H-90)}" r="{r.choice([1, 1.2, 1.6, 2])}" fill="#fff" '
        f'style="animation-delay:{r.uniform(0, 4):.2f}s;animation-duration:{r.uniform(2, 5):.2f}s"/>' for _ in range(70))
    glyphs = ["{ }", "</>", "01", "#", "fn()", "[ ]", "&&", "=>"]
    floaters = "".join(
        f'<text class="fl" x="{90 + i * 145}" y="{H-60}" fill="{PAL[i % 5]}" style="animation-delay:{i * 1.1:.1f}s;animation-duration:{8 + i % 3 * 2}s">{esc(g)}</text>'
        for i, g in enumerate(glyphs))
    roles = CFG["roles"]; n = len(roles); per = 3.2; total = n * per; a = 100 / n
    role_txt = "".join(
        f'<text class="role" x="600" y="262" text-anchor="middle" style="animation-duration:{total}s;animation-delay:{i * per}s">{esc(t)}</text>'
        for i, t in enumerate(roles))
    css = f"""
.tw{{opacity:.15;animation:tw 3s ease-in-out infinite}}@keyframes tw{{0%,100%{{opacity:.1}}50%{{opacity:1}}}}
.b1{{animation:d1 12s ease-in-out infinite alternate}}.b2{{animation:d2 15s ease-in-out infinite alternate}}.b3{{animation:d1 18s ease-in-out infinite alternate-reverse}}
@keyframes d1{{to{{transform:translate(320px,40px)}}}}@keyframes d2{{to{{transform:translate(-300px,-30px)}}}}
.w1{{animation:w 9s linear infinite}}.w2{{animation:w2 14s linear infinite}}
@keyframes w{{to{{transform:translateX(-600px)}}}}@keyframes w2{{to{{transform:translateX(-800px)}}}}
.fl{{font:700 22px {MONO};opacity:0;animation:fl 10s linear infinite}}
@keyframes fl{{0%{{opacity:0;transform:translateY(0)}}15%{{opacity:.55}}85%{{opacity:.2}}100%{{opacity:0;transform:translateY(-230px)}}}}
.hi{{font:600 16px {SANS};letter-spacing:7px;fill:{MUT};animation:rise 1s .1s both}}
.nm{{font:800 78px {SANS};animation:rise 1.1s .35s both}}
.glow{{opacity:.55;animation:rise 1.1s .35s both,pg 3.5s 1.5s ease-in-out infinite}}
@keyframes pg{{50%{{opacity:.9}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(26px)}}to{{opacity:1;transform:none}}}}
.role{{font:600 29px {SANS};fill:{TXT};opacity:0;animation-name:role;animation-iteration-count:infinite;animation-timing-function:ease}}
@keyframes role{{0%{{opacity:0;transform:translateY(16px)}}{a*.12:.1f}%{{opacity:1;transform:none}}{a*.88:.1f}%{{opacity:1;transform:none}}{a:.1f}%{{opacity:0;transform:translateY(-16px)}}100%{{opacity:0}}}}
.bar{{transform-box:fill-box;transform-origin:center;animation:bar 2.4s ease-in-out infinite}}
@keyframes bar{{0%,100%{{transform:scaleX(.35);opacity:.6}}50%{{transform:scaleX(1);opacity:1}}}}
"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(CFG['name'])} — animated header">
<defs><style>{css}</style>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>
{grad('g')}
<filter id="bl" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="55"/></filter>
<filter id="gl" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
<clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<g filter="url(#bl)"><ellipse class="b1" cx="180" cy="110" rx="260" ry="80" fill="{CY}" opacity=".38"/>
<ellipse class="b2" cx="900" cy="90" rx="300" ry="90" fill="{VI}" opacity=".42"/>
<ellipse class="b3" cx="560" cy="200" rx="240" ry="70" fill="{PK}" opacity=".28"/></g>
{stars}{floaters}
<path class="w2" d="{wave(292, 14, 800, 1.2)}" fill="{VI}" opacity=".25"/>
<path class="w1" d="{wave(305, 11, 600, 0)}" fill="{CY}" opacity=".22"/>
<path class="w1" style="animation-duration:6s" d="{wave(322, 9, 600, 2.4)}" fill="{BG}" opacity=".85"/>
<text class="hi" x="600" y="98" text-anchor="middle">HELLO WORLD, I’M</text>
<text class="nm glow" x="600" y="185" text-anchor="middle" fill="url(#g)" filter="url(#gl)">{esc(CFG['name'])}</text>
<text class="nm" x="600" y="185" text-anchor="middle" fill="url(#g)">{esc(CFG['name'])}</text>
{role_txt}
<rect class="bar" x="520" y="284" width="160" height="3" rx="1.5" fill="url(#g)"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="none" stroke="{LINE}"/>
</svg>'''
    save("header.svg", svg)


# ───────────────────────── 2. TERMINAL ─────────────────────────
def terminal():
    W, H = 640, 340
    FS, CW, X0, Y0, STEP = 16, 10.0, 56, 112, 34
    TB = "#0d1226"
    t, events = 0.8, []
    for i, (kind, text) in enumerate(CFG["terminal"]):
        y = Y0 + i * STEP
        if kind == "cmd":
            dur = max(0.6, len(text) * 0.06)
            events.append(dict(kind="cmd", text=text, y=y, start=t, dur=dur)); t += dur + 0.3
        else:
            events.append(dict(kind="out", text=text, y=y, start=t, dur=0.4)); t += 0.8
    cur_y = Y0 + len(CFG["terminal"]) * STEP
    cur_start = t
    T = t + 4.0
    pct = lambda s: s / T * 100
    css = f""".m{{font:{FS}px {MONO}}}.p{{fill:{GR}}}.c{{fill:{TXT}}}.o{{fill:{CY}}}
.cur{{animation:blink 1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}
.dot{{animation:pop 3s ease-in-out infinite}}@keyframes pop{{50%{{transform:scale(1.25)}}}}
"""
    body = ""
    for i, e in enumerate(events):
        s, d = pct(e["start"]), pct(e["dur"])
        if e["kind"] == "cmd":
            n = len(e["text"]); travel = n * CW
            css += (f"@keyframes pf{i}{{0%,{max(s-.01,0):.3f}%{{opacity:0}}{s:.3f}%,100%{{opacity:1}}}}"
                    f"@keyframes ty{i}{{0%,{s:.3f}%{{transform:translateX(0)}}{s+d:.3f}%,100%{{transform:translateX({travel+6:.0f}px)}}}}")
            body += (f'<text class="m p" x="34" y="{e["y"]}" style="opacity:0;animation:pf{i} {T:.2f}s infinite">$</text>'
                     f'<text class="m c" x="{X0}" y="{e["y"]}">{esc(e["text"])}</text>'
                     f'<rect x="{X0}" y="{e["y"]-FS}" width="{W-X0-24}" height="{FS+8}" fill="{TB}" '
                     f'style="animation:ty{i} {T:.2f}s steps({n},end) infinite"/>')
        else:
            css += (f"@keyframes of{i}{{0%,{s:.3f}%{{opacity:0;transform:translateY(5px)}}{s+d:.3f}%,100%{{opacity:1;transform:none}}}}")
            body += f'<text class="m o" x="{X0}" y="{e["y"]}" style="opacity:0;animation:of{i} {T:.2f}s infinite">{esc(e["text"])}</text>'
    s = pct(cur_start)
    css += f"@keyframes cf{{0%,{s:.3f}%{{opacity:0}}{s+.5:.3f}%,100%{{opacity:1}}}}"
    body += (f'<g style="opacity:0;animation:cf {T:.2f}s infinite"><text class="m p" x="34" y="{cur_y}">$</text>'
             f'<rect class="cur" x="{X0}" y="{cur_y-FS+2}" width="10" height="{FS+2}" fill="{CY}"/></g>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Animated terminal introducing {esc(CFG['name'])}">
<defs><style>{css}</style>{grad('tg', W)}</defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="{TB}" stroke="url(#tg)" stroke-width="1.5"/>
<path d="M1 17 a16 16 0 0 1 16 -16 H{W-17} a16 16 0 0 1 16 16 V52 H1 Z" fill="#141b38"/>
<circle class="dot" cx="28" cy="27" r="6" fill="#ff5f57"/><circle class="dot" style="animation-delay:.25s" cx="50" cy="27" r="6" fill="#febc2e"/><circle class="dot" style="animation-delay:.5s" cx="72" cy="27" r="6" fill="#28c840"/>
<text x="{W//2}" y="32" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{MUT}">{esc(CFG['user'].split('-')[0])}@portfolio: ~</text>
{body}</svg>'''
    save("terminal.svg", svg)


# ───────────────────────── 3. ORBIT ─────────────────────────
def orbit():
    S = C = None
    S, C = 560, 280
    radii, durs, dirs = [92, 152, 206], [22, 34, 48], ["normal", "reverse", "normal"]
    css = f"""@keyframes spin{{to{{transform:rotate(360deg)}}}}@keyframes unspin{{to{{transform:rotate(-360deg)}}}}
.ring{{transform-origin:{C}px {C}px;animation:spin 90s linear infinite}}
.core{{transform-box:fill-box;transform-origin:center;animation:pulse 3s ease-in-out infinite}}
@keyframes pulse{{50%{{transform:scale(1.14)}}}}
.halo{{transform-box:fill-box;transform-origin:center;animation:halo 3s ease-out infinite}}
@keyframes halo{{0%{{transform:scale(.8);opacity:.7}}100%{{transform:scale(1.9);opacity:0}}}}
.ct{{font:700 20px {SANS};fill:#fff}}.lb{{font:600 12.5px {SANS};fill:{TXT}}}"""
    rings = items = ""
    k = 0
    for ring, (r, dur, d, labels) in enumerate(zip(radii, durs, dirs, CFG["orbit"])):
        rings += f'<circle class="ring" cx="{C}" cy="{C}" r="{r}" fill="none" stroke="{LINE}" stroke-dasharray="3 9" stroke-width="1.5"/>'
        for j, lab in enumerate(labels):
            col = PAL[k % 5]; k += 1
            delay = -dur * j / len(labels)
            w = len(lab) * 7.6 + 26; x = C + r
            chip = (f'<g style="transform-origin:{x}px {C}px;animation:unspin {dur}s linear infinite {d};animation-delay:{delay:.2f}s">'
                    f'<rect x="{x-w/2:.1f}" y="{C-14}" width="{w:.1f}" height="28" rx="14" fill="{PANEL}" stroke="{col}" stroke-width="1.4"/>'
                    f'<circle cx="{x-w/2+13:.1f}" cy="{C}" r="3.2" fill="{col}"/>'
                    f'<text class="lb" x="{x+5:.1f}" y="{C+4.5}" text-anchor="middle">{esc(lab)}</text></g>')
            items += f'<g style="transform-origin:{C}px {C}px;animation:spin {dur}s linear infinite {d};animation-delay:{delay:.2f}s">{chip}</g>'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}" role="img" aria-label="Tech stack orbiting around a glowing core">
<defs><style>{css}</style>
<radialGradient id="cg"><stop offset="0" stop-color="{VI}"/><stop offset="1" stop-color="{CY}"/></radialGradient>
<radialGradient id="bgo"><stop offset="0" stop-color="{VI}" stop-opacity=".22"/><stop offset="1" stop-color="{VI}" stop-opacity="0"/></radialGradient>
<filter id="g"><feGaussianBlur stdDeviation="6"/></filter></defs>
<circle cx="{C}" cy="{C}" r="{C}" fill="url(#bgo)"/>{rings}
<circle class="halo" cx="{C}" cy="{C}" r="42" fill="none" stroke="{CY}" stroke-width="2"/>
<circle class="core" cx="{C}" cy="{C}" r="44" fill="url(#cg)" filter="url(#g)" opacity=".7"/>
<circle cx="{C}" cy="{C}" r="40" fill="url(#cg)"/>
<text class="ct" x="{C}" y="{C+7}" text-anchor="middle">{esc(CFG['initials'])}</text>{items}</svg>'''
    save("orbit.svg", svg)


# ───────────────────────── 4. MARQUEE ─────────────────────────
def marquee():
    W, H = 1200, 150
    chip_w = lambda s: len(s) * 8.6 + 40
    css = f"@keyframes l{{to{{transform:translateX(var(--d))}}}}.t{{font:600 15px {SANS};fill:{TXT}}}"
    rows = ""
    for ri, items in enumerate(CFG["marquee"]):
        seq = list(items)
        while sum(chip_w(s) + 14 for s in seq) < W + 200:
            seq += items
        setw = sum(chip_w(s) + 14 for s in seq)
        def build(offset):
            x, out = offset, ""
            for i, s in enumerate(seq):
                w = chip_w(s); col = PAL[(i + ri * 2) % 5]
                out += (f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="40" rx="20" fill="{PANEL}" stroke="{col}" stroke-opacity=".8"/>'
                        f'<circle cx="{x+18:.1f}" cy="20" r="4" fill="{col}"/>'
                        f'<text class="t" x="{x+w/2+6:.1f}" y="25.5" text-anchor="middle">{esc(s)}</text>')
                x += w + 14
            return out
        rev = "reverse" if ri % 2 else "normal"
        rows += (f'<g transform="translate(0 {20 + ri * 58})"><g style="--d:-{setw:.1f}px;animation:l {setw/55:.1f}s linear infinite {rev}">'
                 f'{build(0)}{build(setw)}</g></g>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Scrolling list of skills and technologies">
<defs><style>{css}</style>
<linearGradient id="f"><stop offset="0" stop-color="#000"/><stop offset=".08" stop-color="#fff"/><stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
<mask id="m"><rect width="{W}" height="{H}" fill="url(#f)"/></mask></defs>
<g mask="url(#m)">{rows}</g></svg>'''
    save("skills.svg", svg)


# ───────────────────────── 5. PROJECT CARDS ─────────────────────────
def cards():
    W, H = 380, 214
    P = 2 * (W - 4 + H - 4)
    for i, (title, desc, tags, _) in enumerate(CFG["projects"]):
        col = PAL[i % 3]
        css = f"""@keyframes run{{to{{stroke-dashoffset:-{P}}}}}.run{{animation:run 5s linear infinite}}
@keyframes sh{{0%,55%{{transform:translateX(-160px) skewX(-20deg)}}100%{{transform:translateX({W+160}px) skewX(-20deg)}}}}.sh{{animation:sh 5s ease-in-out infinite;animation-delay:{i*.8}s}}
@keyframes bob{{50%{{transform:translate(4px,-4px)}}}}.ar{{animation:bob 1.6s ease-in-out infinite;font:700 22px {SANS};fill:{col}}}
@keyframes fl{{50%{{transform:translateY(-10px)}}}}.fl{{animation:fl 4s ease-in-out infinite}}
.n{{font:800 13px {MONO};fill:{col}}}.h{{font:700 22px {SANS};fill:{TXT}}}.d{{font:14px {SANS};fill:{MUT}}}.tg{{font:600 12px {SANS};fill:{TXT}}}"""
        tx, tagsvg = 26, ""
        for tg in tags:
            w = len(tg) * 7.2 + 22
            tagsvg += (f'<rect x="{tx}" y="{H-52}" width="{w:.1f}" height="26" rx="13" fill="{col}" fill-opacity=".14" stroke="{col}" stroke-opacity=".6"/>'
                       f'<text class="tg" x="{tx+w/2:.1f}" y="{H-34.5}" text-anchor="middle">{esc(tg)}</text>')
            tx += w + 8
        d = "".join(f'<text class="d" x="26" y="{104 + k*22}">{esc(l)}</text>' for k, l in enumerate(desc))
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Project: {esc(title)}">
<defs><style>{css}</style>{grad('g', W)}
<clipPath id="c"><rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18"/></clipPath>
<linearGradient id="s"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="o"><stop offset="0" stop-color="{col}" stop-opacity=".35"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient></defs>
<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18" fill="{PANEL}" stroke="{LINE}"/>
<g clip-path="url(#c)"><circle class="fl" cx="{W-40}" cy="40" r="90" fill="url(#o)"/>
<rect class="sh" x="0" y="0" width="90" height="{H}" fill="url(#s)"/></g>
<rect class="run" x="2" y="2" width="{W-4}" height="{H-4}" rx="18" fill="none" stroke="url(#g)" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="150 {P-150}"/>
<text class="n" x="26" y="44">0{i+1} / PROJECT</text><text class="ar" x="{W-46}" y="48">↗</text>
<text class="h" x="26" y="80">{esc(title)}</text>{d}{tagsvg}</svg>'''
        save(f"project-{i+1}.svg", svg)


# ───────────────────────── 6. BUTTONS ─────────────────────────
def buttons():
    W, H = 290, 66
    specs = [("button-portfolio.svg", "Open Portfolio OS", True), ("button-github.svg", "My GitHub", False), ("button-repo.svg", "Explore PORT-OS", False)]
    for fn, label, filled in specs:
        css = f"""@keyframes ring{{0%{{transform:scale(1);opacity:.7}}100%{{transform:scale(1.14,1.5);opacity:0}}}}
.ring{{transform-box:fill-box;transform-origin:center;animation:ring 2.2s ease-out infinite}}
@keyframes go{{50%{{transform:translateX(7px)}}}}.go{{animation:go 1.3s ease-in-out infinite}}
@keyframes sh{{0%,60%{{transform:translateX(-80px) skewX(-20deg)}}100%{{transform:translateX({W+80}px) skewX(-20deg)}}}}.sh{{animation:sh 3.4s ease-in-out infinite}}
.t{{font:700 17px {SANS};fill:#fff}}"""
        fill = 'url(#g)' if filled else PANEL
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}">
<defs><style>{css}</style>{grad('g', W)}<clipPath id="c"><rect x="6" y="9" width="{W-12}" height="48" rx="24"/></clipPath>
<linearGradient id="s"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<rect class="ring" x="6" y="9" width="{W-12}" height="48" rx="24" fill="none" stroke="{CY}" stroke-width="2"/>
<rect x="6" y="9" width="{W-12}" height="48" rx="24" fill="{fill}" stroke="url(#g)" stroke-width="2"/>
<g clip-path="url(#c)"><rect class="sh" x="0" y="0" width="50" height="{H}" fill="url(#s)"/></g>
<text class="t" x="{W/2-12}" y="38.5" text-anchor="middle">{esc(label)}</text><text class="t go" x="{W-58}" y="39">➜</text></svg>'''
        save(fn, svg)


# ───────────────────────── 7. DIVIDER ─────────────────────────
def divider():
    W, H = 1200, 44
    pts = [f"{x},{22 + 9 * math.sin(2 * math.pi * x / 300):.1f}" for x in range(0, W + 1, 10)]
    d = "M" + " L".join(pts)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="presentation">
<defs><style>@keyframes f{{to{{stroke-dashoffset:-64}}}}.f{{animation:f 2s linear infinite}}</style>{grad('g')}</defs>
<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.5"/>
<path class="f" d="{d}" fill="none" stroke="url(#g)" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="6 26"/>
<circle r="5" fill="{CY}"><animateMotion dur="7s" repeatCount="indefinite" path="{d}"/></circle>
<circle r="11" fill="{CY}" opacity=".25"><animateMotion dur="7s" repeatCount="indefinite" path="{d}"/></circle></svg>'''
    save("divider.svg", svg)


# ───────────────────────── 8. LEARNING BARS ─────────────────────────
def learning():
    W = 1000; rows = CFG["learning"]; H = 30 + len(rows) * 58
    css = f"""@keyframes gr{{0%{{transform:scaleX(0)}}22%,90%{{transform:scaleX(1)}}100%{{transform:scaleX(1);opacity:0}}}}
.fill{{transform-box:fill-box;transform-origin:left center;animation:gr 7s cubic-bezier(.2,.8,.2,1) infinite}}
@keyframes sh{{0%{{transform:translateX(-120px)}}100%{{transform:translateX(900px)}}}}
.l{{font:600 16px {SANS};fill:{TXT}}}.p{{font:700 15px {MONO};fill:{CY}}}"""
    body = ""
    for i, (lab, pct) in enumerate(rows):
        y = 24 + i * 58; bw = 880; fw = bw * pct / 100; col = PAL[i % 5]
        body += (f'<text class="l" x="10" y="{y}">{esc(lab)}</text><text class="p" x="{W-10}" y="{y}" text-anchor="end">{pct}%</text>'
                 f'<rect x="10" y="{y+12}" width="{W-20}" height="14" rx="7" fill="{PANEL}" stroke="{LINE}"/>'
                 f'<g clip-path="url(#cl{i})"><rect class="fill" style="animation-delay:{i*.25}s" x="10" y="{y+12}" width="{(W-20)*pct/100:.1f}" height="14" rx="7" fill="{col}"/></g>'
                 f'<clipPath id="cl{i}"><rect x="10" y="{y+12}" width="{(W-20)*pct/100:.1f}" height="14" rx="7"/></clipPath>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Animated progress bars for current learning focus">
<defs><style>{css}</style></defs>{body}</svg>'''
    save("learning.svg", svg)


# ───────────────────────── 9. CODE-RAIN GIF ─────────────────────────
def footer_gif():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow not installed — skipping footer.gif (pip install pillow)"); return
    W, H, FS = 900, 180, 15
    def font(paths, size):
        for p in paths:
            try: return ImageFont.truetype(p, size)
            except OSError: pass
        return ImageFont.load_default()
    mono = font(["DejaVuSansMono.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "Consolas.ttf", "Menlo.ttc"], FS)
    bold = font(["DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"], 30)
    small = font(["DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "Arial.ttf"], 14)
    cols, rows, trail = W // 14, H // FS, 10
    P = rows + trail
    r = random.Random(3)
    offs = [r.randrange(P) for _ in range(cols)]
    spd = [r.choice([0.5, 1]) for _ in range(cols)]
    glyph = [[r.choice("01{}<>/;=+*#$%&") for _ in range(P)] for _ in range(cols)]
    frames = []
    for f in range(2 * P):
        img = Image.new("RGBA", (W, H), (11, 16, 32, 255)); d = ImageDraw.Draw(img)
        for c in range(cols):
            head = int(offs[c] + f * spd[c]) % P
            for t in range(trail):
                row = head - t
                if 0 <= row < rows:
                    k = 1 - t / trail
                    col = (255, 255, 255) if t == 0 else (int(34 * k + 8), int(211 * k + 10), int(238 * k + 20))
                    d.text((c * 14 + 2, row * FS), glyph[c][(row + c) % P], font=mono, fill=col)
        band = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
        bd.rounded_rectangle((W // 2 - 270, H // 2 - 46, W // 2 + 270, H // 2 + 46), 20, fill=(11, 16, 32, 215), outline=(34, 211, 238, 255), width=2)
        img = Image.alpha_composite(img, band); d = ImageDraw.Draw(img)
        t1, t2 = "THANKS FOR STOPPING BY", "let’s build something together"
        d.text((W // 2, H // 2 - 14), t1, font=bold, fill=(230, 237, 247), anchor="mm")
        d.text((W // 2, H // 2 + 24), t2, font=small, fill=(139, 154, 184), anchor="mm")
        frames.append(img.convert("RGB").quantize(64, method=Image.Quantize.MEDIANCUT))
    frames[0].save(OUT / "footer.gif", save_all=True, append_images=frames[1:], duration=90, loop=0, optimize=True, disposal=2)


# ───────────────────────── 10. README ─────────────────────────
def readme():
    u, a = CFG["user"], "assets"
    proj = "".join(
        f'<td align="center" width="33%"><a href="{p[3]}"><img src="{a}/project-{i+1}.svg" alt="{esc(p[0])}" width="100%"/></a></td>'
        for i, p in enumerate(CFG["projects"]))
    snake = f"https://raw.githubusercontent.com/{u}/{u}/output"
    md = f'''<div align="center">

<img src="{a}/header.svg" alt="{esc(CFG['name'])} — animated header" width="100%"/>

<a href="{CFG['portfolio']}"><img src="{a}/button-portfolio.svg" alt="Open Portfolio OS" height="56"/></a>
<a href="https://github.com/{u}"><img src="{a}/button-github.svg" alt="My GitHub" height="56"/></a>
<a href="https://github.com/{u}/PORT-OS"><img src="{a}/button-repo.svg" alt="Explore PORT-OS" height="56"/></a>

<img src="https://komarev.com/ghpvc/?username={u}&style=for-the-badge&color=22d3ee&labelColor=0b1020&label=PROFILE+VIEWS" alt="Profile views"/>

<img src="{a}/divider.svg" alt="" width="100%"/>

</div>

<table align="center">
<tr>
<td width="55%" valign="middle"><img src="{a}/terminal.svg" alt="Animated terminal" width="100%"/></td>
<td width="45%" valign="middle"><img src="{a}/orbit.svg" alt="Tech stack orbit" width="100%"/></td>
</tr>
</table>

<div align="center"><img src="{a}/divider.svg" alt="" width="100%"/></div>

<details open>
<summary><b>About me</b> <i>(click to collapse)</i></summary>

- I’m a **B.Tech CSE student** who loves building things for the web and exploring machine learning.
- I’m currently building **[PORT-OS]({CFG['portfolio']})**, a portfolio that behaves like an operating system.
- I’m always happy to collaborate on open-source and learning projects.

</details>

<details>
<summary><b>Quick links</b> <i>(click to expand)</i></summary>

- Portfolio: [{CFG['portfolio'].replace('https://', '')}]({CFG['portfolio']})
- GitHub: [@{u}](https://github.com/{u})
<!-- Add LinkedIn / email / Instagram here once you want them on your profile -->

</details>

<div align="center">

## Tech stack
<img src="{a}/skills.svg" alt="Skills and technologies" width="100%"/>

## Featured projects
<table><tr>{proj}</tr></table>

## Currently exploring
<img src="{a}/learning.svg" alt="Current learning focus" width="85%"/>

## Contribution snake
Every green square is a snack for the snake.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{snake}/github-snake-dark.svg"/>
  <source media="(prefers-color-scheme: light)" srcset="{snake}/github-snake.svg"/>
  <img alt="Animated contribution snake" src="{snake}/github-snake-dark.svg" width="100%"/>
</picture>

<img src="{a}/footer.gif" alt="Thanks for stopping by" width="100%"/>

</div>
'''
    (ROOT / "README.md").write_text(md, encoding="utf-8")


if __name__ == "__main__":
    for fn in (header, terminal, orbit, marquee, cards, buttons, divider, learning, footer_gif, readme):
        fn(); print("built", fn.__name__)
