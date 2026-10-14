---
name: procedural-motion-graphics
description: Use when creating procedural motion graphics, 9:16 vertical mobile social video ads (V4 golden standard), kinetic typography, animated UI product simulations, procedural DSP electronic soundtracks, or vector animations in pure Python without external video editors.
---

# Procedural Motion Graphics in Python

This skill equips agents with end-to-end expertise in generating broadcast-grade motion graphics entirely from code. Every frame is a deterministic mathematical function of time $t$, allowing 100% reproducible rendering in pure Python (Pillow + NumPy + SciPy) encoded directly to H.264 via `imageio-ffmpeg` or `ffmpeg` CLI—with zero reliance on After Effects, Blender, or stock assets.

---

## 1. Quick Capabilities & Runbook

| Task | Command / Script | Reference |
| :--- | :--- | :--- |
| **Vertical Mobile Ad (V4 Golden Standard)** | `python examples/08_vertical_social_ad_simulation.py` | 1080x1920, 5-act narrative, push-stack hook, touch taps, keyboard, toasts, DSP audio |
| **Instant Keyframe Preview (V4)** | `python examples/08_vertical_social_ad_simulation.py --preview 1.7 5.2 9.0 11.5 14.5` | Fast visual debugging in 0.5s |
| **Procedural DSP Audio Synthesizer** | `python scripts/x_ad_audio.py` | Synthesizes 15s stereo DSP soundtrack + UI Foley to WAV |
| **Horizontal App UI & Resume (V3)** | `python examples/07_app_ui_product_simulation.py` | Synced lyrics, vertical app swipe, EQ bars, cursor click ripple |
| **Flat Wrapped Editorial (V2)** | `python examples/06_flat_wrapped_editorial.py` | SSAA 1.5x, spring physics, polar morph, iris wipe |
| **Instant Frame Preview** | `python scripts/preview_frame.py --time 1.2 -o preview.png` | Fast visual debugging in 0.5s |
| **Render All Scene Stills** | `python scripts/preview_frame.py --all-scenes` | Generates keyframe PNGs in `assets/` or `previews/` |
| **Render Full Showreel** | `python scripts/render_showreel.py showreel.mp4 --fps 30` | 1080p @ 30fps H.264 render |
| **Kinetic Title Quickstart** | `python examples/01_quickstart_kinetic_title.py` | 3s title sequence with bounce & bloom |
| **3D Particle Orbit** | `python examples/03_orbital_particles_3d.py` | Perspective 3D particles & depth sort |

---

## 2. Architectural Evolution: V1 $\to$ V2 $\to$ V3 $\to$ V4

| Dimension | Version 1 (`X ad 1` Desktop) | Version 2 (`X ad 2` Mobile Prototype) | Version 3 (`X ad 3` Minimalist Feed) | Version 4 (`X ad 4` - Desired Golden Standard) |
| :--- | :--- | :--- | :--- | :--- |
| **Aspect Ratio & Resolution** | 1920x1080 (16:9 Landscape) | 1080x1920 (9:16 Vertical) | 720x1280 (9:16 Vertical) | **1080x1920 Full HD (9:16 Vertical)** |
| **Visual Tone & World** | Sci-Fi 3D wireframe grid & floating dust | Mobile UI simulation with static text boxes & HUD clutter | Minimal flat feed scroll, text-only posts | **Surgical minimalism on pure `#000000` black + hyper-authentic native mobile OS screens** |
| **Anti-Aliasing & Blits** | 1x standard PIL (aliased) | 1.5x SSAA Lanczos, full-frame RGBA blits | 1.5x SSAA Lanczos (Pen class) | **1.5x SSAA Lanczos + 1-Channel `"L"` Bounded Alpha Blits (`_alpha`) + `paste_rounded`** |
| **Narrative Copy Overlays** | None | Cluttered sci-fi telemetry & analytics boxes | None | **Floating narrative pill captions (`caption()`): *"See it first."*, *"Say it your way."*, *"Get heard."*** |
| **Interactivity & Gestures** | None (pure broadcast video) | Touch tap indicator, heart scale pop, button 8% depression | Simplified heart pop, outline button ripple | **Touch tap indicator (pad + compression dip + shockwave ripple), QWERTY key pop magnification, 8-particle burst on like** |
| **Modals & Transitions** | Hard cuts / slides | Single vertical push; hardcoded modal coordinates | Hard flash cuts | **Compositor-level transitions (`apply_transition`): `push`, `sheet_up` (over dimmed feed), `sheet_down`, `zoom`** |
| **Feedback & Continuity** | None | Cluttered analytics card, generic toasts | None | **Native `Post` detail view, exponential counter ramping (284K+), floating hearts, 3 character-continuous toasts, bell badge to "99+"** |
| **Audio Engine** | Naive NumPy synth, ambient drone | Initial SciPy SOS filter integration | Minimal mono chiptune-style audio in single file | **Stereo 120 BPM DSP in A minor: 3-voice detuned 12-harmonic `saw` pad, filter sweep (`700->2400Hz`), `riser`, flutter `clap`, 16th-note `pluck` arp, kick side-chain ducking, UI Foley** |
| **Render Engine** | Single-threaded | Monolithic single-threaded | Single-threaded | **Multi-core parallel processing (`multiprocessing.Pool`), chunked pipes to ffmpeg, fast CLI `--preview`** |

---

## 3. The Design Pillars

### Pillar 1: Full-HD Vertical Mobile Product Ad & Procedural DSP Audio (V4 - Desired Golden Standard)
- **Concept**: **"The Product IS the Commercial"**. Native 1080x1920 9:16 vertical commercial designed for high-conversion social feeds (TikTok, Instagram Reels, YouTube Shorts, X Timeline).
- **5-Act Narrative Arc**:
  1. **Act 1: The Kinetic Hook ($0.00 - 3.05\text{s}$)**: Centered brand logo + pulsing `"Happening now"` chip. Four hook phrases (`"Breaking news."`, `"Live sports."`, `"Hot takes."`, `"Big ideas."`) spawn at `base_y = 1020`, physically pushing older lines upward (`LHH = 178px`) while aging them to dark grey `(58, 61, 64)` and showing a blue trending sub-label only on the newest line. At $2.05\text{s}$, all stack lines flush upward (`exit_k`) for the 2-line hero slam (`"It's all"` / `"happening."`) with exponential scale settle and underline sweep.
  2. **Act 2: The Native Feed ($3.05 - 7.55\text{s}$)**: Enters via `vertical_push_transition`. Displays 5 dynamically wrapped posts (`layout_post`) with per-second live incrementing counters (`rate`) and 3 isolated sub-canvas media cards (`media_rocket`, `media_score`, `media_sunset`) rendered with `vgrad` and `paste_rounded`. Two-stage scroll (`SCROLL1` centers `Maya Chen`'s text post for the `LIKE_T = 1.95s` touch tap + heart pop + particle burst; `SCROLL2` reveals soccer scoreboard and sunset cards), overlaid by the floating pill caption `"See it first."`, ending with a tap on the floating `+` Compose FAB.
  3. **Act 3: Compose Sheet Modal ($7.55 - 10.05\text{s}$)**: Enters via compositor-level `sheet_up` over the dimmed Act 2 feed (`dim(prev, 0.6 * p)`) while keeping the top 100px iOS status bar fixed. Starts with the grey `"What's happening?"` placeholder and a dark disabled `"Post"` button `(14, 72, 112)` for the first $0.45\text{s}$, which illuminates to vibrant `#1D9BF0` as live typing begins (`"Hello, X. What's everyone talking about?"`). Features the floating pill caption `"Say it your way."`, vector globe/media/GIF/poll/pin icons, circular character counter arc, and a full QWERTY keyboard with `ease_out_back` key pop magnification and vector `⇧`/`⌫` keys.
  4. **Act 4: Viral Payoff ($10.05 - 12.05\text{s}$)**: Enters via `sheet_down` into the clean native `<- Post` detail screen (no fake analytics chart clutter). Views (`284K`), Reposts (`1.8K`), Quotes (`128`), and Likes (`12.4K`) ramp via `ease_out_expo`. Ten translucent hearts (`alpha_poly`) drift 180px upward from the heart icon without colliding with post text. Three staggered notification toasts slide in from the right (`dx = (1 - e) * 260`), reusing the exact characters from Act 2 (`Maya Chen`, `Goal Line`, `86 new followers`) for narrative continuity, paired with `"Get heard."` and the bottom-nav bell badge climbing from `3` to `"99+"`.
  5. **Act 5: Monumental Climax & CTA ($12.05 - 15.00\text{s}$)**: Enters via `zoom` transition (`1.0 -> 1.15x` cross-blend) into a pure black canvas illuminated by a continuous 2D Gaussian `float32` radial glow (`glow_map()`). The exact 12-vertex SVG X logo (`XL_OUT` / `XL_HOLE`) pops in with `ease_out_back` and dual expanding shockwave rings, followed by `"Join the conversation."`, a white pill CTA button (`"Get the app"`, depressed 8% by an off-center touch tap at `(640, 1300)`), and `"x.com"`.
- *Deep dives: [references/vertical-mobile-ad-architecture.md](./references/vertical-mobile-ad-architecture.md) & [references/procedural-audio-dsp-and-sound-design.md](./references/procedural-audio-dsp-and-sound-design.md)*

### Pillar 2: Horizontal App UI & Product Simulation (V3)
- **Concept**: **"The Resume IS the App"**. Recreates interactive desktop/tablet music app screens in 16:9 landscape ($1280\times 720$) with synced lyrics, `mini_eq_bars`, and `generative_cover`.
- *Deep dive: [references/app-ui-and-product-simulation.md](./references/app-ui-and-product-simulation.md)*

### Pillar 3: Flat Editorial / "Spotify Wrapped" (V2)
- **Visual Style**: Saturated color-block scenes, hard offset shadows (`+8, +8`), damped harmonic springs (`spring(x, k=7, w=14)`), polar shape morphs, and circular `iris_wipe` transitions.
- *Deep dive: [references/polar-shape-morphing-and-ui.md](./references/polar-shape-morphing-and-ui.md)*

### Pillar 4: Dark Cyber Glow Compositing (V1)
- **Visual Style**: Midnight navy backgrounds (`#080812`), Lissajous radial glows, 3D orbital particles, Gaussian bloom, chromatic aberration, and film grain.
- *Deep dive: [references/compositing-pipeline.md](./references/compositing-pipeline.md)*

---

## 4. The 10 V4 Golden Rules & Anti-Patterns (Must Follow)

When building a V4 vertical mobile product ad, strictly adhere to these 10 engineering and art-direction rules:

| # | Golden Standard Rule (`X ad 4`) | Anti-Pattern to Avoid |
| :--- | :--- | :--- |
| **1** | **Surgical Negative Space**: Keep Act 1 and Act 5 on pure `#000000` black. In Acts 2–4, render *only* authentic native app UI plus a single floating `caption()` pill. | Adding sci-fi radar rings, `0.02s LATENCY` badges, telemetry HUDs, or fake "Analytics Dashboard" line-chart cards that clutter the screen. |
| **2** | **Cumulative Hook Push-Stack (`pushes` + `age` + `exit_k`)**: Spawn each hook phrase at `base_y = 1020`, push prior phrases up by `LHH = 178`, dim older lines to `(58, 61, 64)`, show the trending sub-label *only* on the newest line, and eject all lines (`exit_k`) before the final 2-line slam. | Drawing all hook words at fixed static Y coordinates simultaneously like a poster, or stacking 3 large cards at the bottom of Act 1. |
| **3** | **Compositor-Level Transitions (`apply_transition`)**: Keep scene functions (`scene_feed`, `scene_compose`, `scene_reaction`, `scene_end`) pure and apply `push`, `sheet_up` (over `dim(prev, 0.6*p)`), `sheet_down`, and `zoom` in `frame_at(t)`. | Hardcoding slide offsets inside scene functions or using a fake grey rectangle at the top of the modal instead of dimming the actual previous frame. |
| **4** | **Isolated Sub-Canvas Media (`vgrad` + `paste_rounded`)**: Draw each feed media card on its own `Canvas(w, h)`, fill sky/turf/sea backgrounds with `vgrad` (`np.interp`), and composite onto the feed with `paste_rounded(sub, x, y, r=32)`. | Drawing rockets, smoke, or confetti directly onto the main feed canvas where particles can bleed outside card borders or require manual Y clipping. |
| **5** | **1-Channel `"L"` Mask Bounded Alpha (`_alpha`)**: Allocate only a 1-channel grayscale mask `Image.new("L", (X1-X0, Y1-Y0), 0)` and call `self.im.paste(color, (X0, Y0, X1, Y1), m)`. | Allocating 4-channel `RGBA` overlays, converting to `RGB`, and splitting alpha channels on every translucent shape (4x slower). |
| **6** | **Responsive Typography (`fit_size` & `wrap`)**: Compute dynamic font sizes via `fit_size(texts, weight, maxw, max_size)` and line breaks via `wrap(text, size, weight, maxw)`, and position inline badges using measured text width `tw()`. | Hardcoding X offsets for verified badges or hashtag highlights, or manually splitting multi-line strings. |
| **7** | **Authentic Compose State Progression**: Show `"What's happening?"` in grey and a dark disabled `"Post"` button `(14, 72, 112)` during `0.00 - 0.45s` before typing starts; transition `"Post"` to `#1D9BF0` as the first character is typed. | Rendering the `"Post"` button 100% bright from frame zero, skipping the placeholder, or adding extra cards inside the compose modal. |
| **8** | **Cross-Act Character Continuity**: Reuse the exact characters introduced in the Act 2 feed (`Maya Chen`, `Goal Line`) inside the Act 4 notification toasts (`"Maya Chen and 1,208 others liked your post"`, `"Goal Line reposted your post"`). | Inventing disconnected generic toast text that breaks the story arc between the feed and the viral reaction. |
| **9** | **Exact Brand Geometry & Continuous `glow_map`**: Render the X logo using the exact 12-vertex SVG coordinates (`XL_OUT` and `XL_HOLE`), the verified badge using an 8-lobe polar cosine (`1 + 0.09*cos(8*a)`), and the Act 5 backdrop using a 2D `float32` Gaussian `np.exp(-d2)` array. | Approximating the X logo with 2 rough parallelograms, using a plain circle for the verified badge, or drawing glow with discrete concentric circles (Mach banding). |
| **10** | **Progressive Stereo DSP Arrangement**: Use 12-harmonic `saw()` with 3-voice semitone detune (`-0.12, 0, +0.11`), a 1s `riser()` into Act 2, 3-burst flutter `clap()` (`0, 11, 23ms`), 8th-note octave bass in Act 2, and a stereo-panned 16th-note `pluck()` arpeggiator in Act 3. | Using plain sine-wave pads, static noise whooshes, or a flat drum loop without musical evolution across acts. |

---

## 5. Essential V4 Code Patterns (`Canvas`, Transitions & Brand Geometry)

### 5.1 SSAA `Canvas` with 1-Channel Bounded Alpha, `vgrad`, and `paste_rounded`
```python
class Canvas:
    """1.5x Super-Sampled drawing surface; all coordinates are in 1080x1920 output pixels."""
    def __init__(self, bg=(0, 0, 0), w=1080, h=1920, k=1.5):
        self.bg, self.w, self.h, self.k = bg, w, h, k
        self.im = Image.new("RGB", (int(w * k), int(h * k)), bg)
        self.d = ImageDraw.Draw(self.im)

    def _alpha(self, x0, y0, x1, y1, color, a, draw_fn):
        a = clamp(a)
        if a <= 0:
            return
        X0, Y0 = max(0, int(math.floor(x0 * self.k)) - 2), max(0, int(math.floor(y0 * self.k)) - 2)
        X1, Y1 = min(self.im.size[0], int(math.ceil(x1 * self.k)) + 2), min(self.im.size[1], int(math.ceil(y1 * self.k)) + 2)
        if X1 <= X0 or Y1 <= Y0:
            return
        m = Image.new("L", (X1 - X0, Y1 - Y0), 0)
        draw_fn(ImageDraw.Draw(m), X0, Y0, int(255 * a))
        self.im.paste(color, (X0, Y0, X1, Y1), m)

    def paste_rounded(self, sub, x0, y0, r):
        m = Image.new("L", sub.im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, sub.im.size[0] - 1, sub.im.size[1] - 1],
                                            radius=r * self.k, fill=255)
        self.im.paste(sub.im, (int(x0 * self.k), int(y0 * self.k)), m)

    def render(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)

def vgrad(c: Canvas, stops):
    """Fill a canvas with a vertical multi-stop gradient: stops=[(pos, (r,g,b)), ...]."""
    hpx, wpx = c.im.size[1], c.im.size[0]
    y = np.linspace(0, 1, hpx)
    cols = np.zeros((hpx, 3), np.float32)
    for ch in range(3):
        cols[:, ch] = np.interp(y, [s[0] for s in stops], [s[1][ch] for s in stops])
    c.im.paste(Image.fromarray(np.repeat(cols[:, None, :], wpx, axis=1).astype(np.uint8)))
```

### 5.2 Exact SVG X Logo (`XL_OUT` / `XL_HOLE`) & 8-Lobe Verified Rosette (`badge`)
```python
XL_OUT = [(18.244, 2.25), (21.552, 2.25), (14.325, 10.51), (22.827, 21.75), (16.17, 21.75),
          (10.956, 14.933), (4.99, 21.75), (1.68, 21.75), (9.41, 12.915), (1.254, 2.25),
          (8.08, 2.25), (12.793, 8.481)]
XL_HOLE = [(17.083, 19.77), (18.916, 19.77), (7.084, 4.126), (5.117, 4.126)]

def xlogo(c: Canvas, cx: float, cy: float, size: float, col=(255, 255, 255), bg=(0, 0, 0)):
    s = size / 21.6
    f = lambda p: (cx + (p[0] - 12.04) * s, cy + (p[1] - 12.0) * s)
    c.poly([f(p) for p in XL_OUT], fill=col)
    c.poly([f(p) for p in XL_HOLE], fill=bg)

def badge(c: Canvas, cx: float, cy: float, r: float, col=(29, 155, 240)):
    pts = [(cx + math.cos(2*math.pi*i/96) * r * (1 + 0.09 * math.cos(8 * 2*math.pi*i/96)),
            cy + math.sin(2*math.pi*i/96) * r * (1 + 0.09 * math.cos(8 * 2*math.pi*i/96))) for i in range(96)]
    c.poly(pts, fill=col)
    c.line([(cx - r*0.42, cy + r*0.02), (cx - r*0.12, cy + r*0.32), (cx + r*0.44, cy - r*0.30)], (255, 255, 255), r*0.24)
```

---

## 6. Design Guidelines for New Motion Projects

1. **Default to Vertical Mobile Product Simulation (V4)**: When creating social ads, app launches, or feature announcements, choose 1080x1920 vertical format with the 5-Act framework (`Hook -> Feed -> Compose -> Reaction -> End Card`).
2. **Always Use Super-Sampled Anti-Aliasing (SSAA)**: Never draw at native 1x resolution. Use $K=1.5$ with Lanczos downsampling and 1-channel `"L"` bounded alpha masks (`_alpha`).
3. **Preview Keyframes Before Full Render**: Always run `--preview 1.7 5.2 9.0 11.5 14.5` and inspect the PNG stills for text collisions, badge alignment, and negative space before encoding all 450 frames.
4. **Synthesize Procedural Audio with Progressive Arrangement & Side-Chain Ducking**: Build energy across acts (700Hz pad $\to$ riser $\to$ 2400Hz pad + octave bass + flutter clap $\to$ 16th-note pluck arp $\to$ sub-drop impact) with kick side-chain ducking and frame-accurate UI Foley.
5. **Accelerate with Multi-Core Parallel Rendering**: Use `multiprocessing.Pool` with chunked pipes into `imageio-ffmpeg` or `ffmpeg` CLI.
