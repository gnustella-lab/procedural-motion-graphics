---
name: procedural-motion-graphics
description: >-
  Create broadcast-grade procedural motion graphics, kinetic typography, 2D/3D
  particle systems, geometric morphs, and video showreels in pure Python
  (NumPy + Pillow + imageio-ffmpeg) without external video editing software.
  Supports Full-HD Vertical Mobile Product Ads & Procedural DSP Audio (V4 Desired Architecture),
  Horizontal App UI Simulations, Flat Editorial / "Spotify Wrapped" vectors, and Dark Cyber Glow.
---

# Procedural Motion Graphics in Python

This skill equips agents with end-to-end expertise in generating broadcast-grade motion graphics entirely from code. Every frame is a deterministic mathematical function of time $t$, allowing 100% reproducible rendering in pure Python (Pillow + NumPy + SciPy) encoded directly to H.264 via `imageio-ffmpeg`—with zero reliance on After Effects, Blender, or stock assets.

---

## 1. Quick Capabilities & Runbook

| Task | Command / Script | Reference |
| :--- | :--- | :--- |
| **Vertical Mobile Ad (V4 Desired)** | `python examples/08_vertical_social_ad_simulation.py` | 1080x1920, 5-act narrative, touch taps, keyboard, toasts, DSP audio |
| **Horizontal App UI & Resume (V3)** | `python examples/07_app_ui_product_simulation.py` | Synced lyrics, vertical app swipe, EQ bars, cursor click ripple |
| **Flat Wrapped Editorial (V2)** | `python examples/06_flat_wrapped_editorial.py` | SSAA 1.5x, spring physics, polar morph, iris wipe |
| **Instant Frame Preview** | `python scripts/preview_frame.py --time 1.2 -o preview.png` | Fast visual debugging in 0.5s |
| **Render All Scene Stills** | `python scripts/preview_frame.py --all-scenes` | Generates keyframe PNGs in `assets/` or `previews/` |
| **Render Full Showreel** | `python scripts/render_showreel.py showreel.mp4 --fps 30` | 1080p @ 30fps H.264 render |
| **Kinetic Title Quickstart** | `python examples/01_quickstart_kinetic_title.py` | 3s title sequence with bounce & bloom |
| **3D Particle Orbit** | `python examples/03_orbital_particles_3d.py` | Perspective 3D particles & depth sort |

---

## 2. Architectural Evolution: V1 $\to$ V2 $\to$ V3 $\to$ V4

| Dimension | Version 1 (Dark Cyber) | Version 2 (Landscape App) | Version 3 (Minimal Feed) | Version 4 (Full-HD Vertical Ad - Desired) |
| :--- | :--- | :--- | :--- | :--- |
| **Aspect Ratio** | 1920x1080 (16:9 Landscape) | 1920x1080 (16:9 Landscape) | 720x1280 (9:16 Vertical) | **1080x1920 Full HD (9:16 Vertical)** |
| **Visual World** | Sci-Fi grid & floating dust | Glassmorphism post in vacuum | Minimal flat feed scroll | **Hyper-realistic native mobile OS & timeline** |
| **Anti-Aliasing** | 1x standard PIL (aliased) | 1x standard PIL (aliased) | 1.5x SSAA Lanczos | **1.5x SSAA Lanczos + Bounded Alpha Blits** |
| **Interactivity** | None | Desktop mouse cursor | Feed scroll | **Touch tap indicator (pad + dip + shockwave ripple)** |
| **Modals & Keyboard**| None | None | None | **Slide-up bottom sheet modal, QWERTY key pop magnification** |
| **Feedback Alerts** | None | None | None | **Ramping live metrics, floating hearts, sliding toast alerts, bell "99+"** |
| **Audio Engine** | Naive NumPy synth, mono | 128 BPM electronic, mono | Basic 4-chord pad, mono | **Stereo binaural DSP with SciPy Butterworth filters, side-chain ducking, UI Foley** |
| **Render Engine** | Single-threaded | Single-threaded | Single-threaded | **Multi-core parallel processing (`multiprocessing.Pool`), CLI `--preview`** |

---

## 3. The Design Pillars

Choose the design pillar that fits the project brief:

### Pillar 1: Full-HD Vertical Mobile Product Ad & Procedural DSP Audio (V4 - Desired & Recommended)
- **Concept**: **"The Product IS the Commercial"**. Native 1080x1920 9:16 vertical commercial designed for high-conversion social feeds (TikTok, Instagram Reels, YouTube Shorts, X Timeline).
- **5-Act Narrative Arc**:
  1. **Act 1: The Kinetic Hook ($0.0 - 3.0\text{s}$)**: Exponential kinetic typography slammed onto the screen with pulsing live chips ("Happening Now") and underline sweeps.
  2. **Act 2: The Native Feed ($3.0 - 7.5\text{s}$)**: Realistic timeline feed with momentum scroll physics, procedural animated media cards (rocket launches with procedural smoke/flame, sports scoreboards with live confetti), and authentic touch tap indicators triggering heart scale pops and particle bursts.
  3. **Act 3: Compose Sheet Modal ($7.5 - 10.0\text{s}$)**: Modal slide-up (`sheet_up`) over dimmed background, full QWERTY keyboard with active key magnification pop-up, live typing ticks, and Post button tap ripple.
  4. **Act 4: Viral Payoff ($10.0 - 12.0\text{s}$)**: Explosive counter metrics, floating heart physics, staggered incoming notification toasts sliding in from the right, and bottom nav notification badge climbing to "99+".
  5. **Act 5: Monumental Climax & CTA ($12.0 - 15.0\text{s}$)**: Zoom cut into dark canvas, brand logo reveal with dual expanding shockwaves and radial glow, tactile CTA button click depression (8%), and ripple.
- **Procedural Audio DSP Engine**:
  - Pure Python synthesis with NumPy & SciPy Butterworth filters (`scipy.signal.butter` / `sosfilt`).
  - Side-chain ducking: Kick triggers exponential envelope ducking on the synth pad and bass.
  - Frame-accurate UI Foley sound design: word slam ticks, transition whooshes, touch tap clicks, heart pop bubbles, keystroke tick-clacks, post send whoosh, ascending notification chimes, and sub-drop impact booms.
- *Deep dives: [references/vertical-mobile-ad-architecture.md](./references/vertical-mobile-ad-architecture.md) & [references/procedural-audio-dsp-and-sound-design.md](./references/procedural-audio-dsp-and-sound-design.md)*

### Pillar 2: Horizontal App UI & Product Simulation (V3)
- **Concept**: **"The Resume IS the App"**. The video recreates the interactive screens of a modern music app (Spotify/Apple Music) in 16:9 landscape ($1280\times 720$).
- **Features**: Synced karaoke lyrics, playlist tracklists with 3-bar animated green equalizer bars (`mini_eq_bars`), generative geometric album covers, and desktop mouse pointer click depression.
- *Deep dive: [references/app-ui-and-product-simulation.md](./references/app-ui-and-product-simulation.md)*

### Pillar 3: Flat Editorial / "Spotify Wrapped" (V2)
- **Visual Style**: Saturated solid color-block scenes (Green, Purple, Orange, Blue, Black), bold typography with hard offset shadows (`+8, +8`), bouncing polar shape morphs with squash & stretch and contact shadows.
- **Physics**: Damped harmonic springs (`spring(x, k=7, w=14)`).
- **Transitions**: Concurrent circular iris wipes (`iris_wipe`).
- *Deep dive: [references/polar-shape-morphing-and-ui.md](./references/polar-shape-morphing-and-ui.md)*

### Pillar 4: Dark Cyber Glow Compositing (V1)
- **Visual Style**: Midnight navy backgrounds (`#080812`), Lissajous radial gradient glows, neon typography with chromatic 3D extrusions, and 3D orbital particle clouds.
- **Post Pipeline**: Downsampled Gaussian bloom pass, chromatic aberration spikes on cuts, and film grain.
- *Deep dive: [references/compositing-pipeline.md](./references/compositing-pipeline.md)*

---

## 4. Core Architecture: Super-Sampled Frame Rendering (SSAA)

To eliminate CPU rasterization stair-stepping, always render through `Pen` or `Canvas` with a $1.5\times$ super-sampling factor ($K=1.5$) and Lanczos downsampling:

```python
import numpy as np
from PIL import Image
from scripts.motion_engine import Pen, ease_out_cubic, prog

W, H, FPS = 1080, 1920, 30

def render_scene(t: float) -> Image.Image:
    pen = Pen("#000000", W, H, k=1.5)
    e = ease_out_cubic(prog(t, 0.2, 0.9))
    pen.txt(540, 960 + (1.0 - e) * 40, "SEE WHAT'S HAPPENING", 36, (255, 255, 255), anchor="mm")
    return pen.render()
```

---

## 5. Modular Toolkit (`scripts/motion_engine.py`)

### 5.1 Mobile App UI & Interactive Micro-Interactions (V4)
- `vertical_push_transition(curr, prev, progress)`: Mobile/desktop vertical screen push swipe.
- `horizontal_push_transition(curr, prev, progress)`: Horizontal screen swipe.
- `button_click_press(t, t_click)`: Tactile 8% button scale depression on click.
- `draw_click_ripple(pen, cx, cy, t, t_click)`: Expanding circular shockwave ripple.
- `mini_eq_bars(pen, x, y, t, color, count=3)`: Animated 3-bar green equalizer for active playlist tracks.
- `generative_cover(pen, x, y, size, seed, color)`: Algorithmic geometric album art with seeded variations.

### 5.2 Spring Physics & Easings
- `ease_out_cubic(x)` & `ease_in_out_cubic(x)`: Penner cubic easings for responsive UI motion.
- `ease_out_back(x, s=1.8)`: Controlled UI card/avatar pop-in overshoot.
- `ease_out_expo(x)` & `ease_in_expo(x)`: Exponential fast-snap easings for kinetic typography.
- `spring(x, k=7, w=14)`: Damped harmonic spring oscillation.
- `smoothstep(x)`: Hermite cubic S-curve for wipes and fills.
- `squash_and_stretch(bounce)`: Deform scale $(s_x, s_y)$ on impact.

### 5.3 Vector Canvas (`Pen`)
- `Pen(bg, width, height, k=1.5)`: Manages $1.5\times$ super-sampled canvas, font loading, coordinate scaling, and Lanczos export.

### 5.4 2D Polar Shape Morphing
- `polar_radius(shape, theta)` & `morph_polar_shapes(a, b, progress)`: Continuous shape morphing across Circle, Square, Triangle, and Star without inverted topology.

### 5.5 3D Perspective Projection & Compositing
- `rotate_3d` & `project_3d`: 3D Euler rotations and perspective division.
- `apply_glow_bloom`, `apply_chromatic_aberration`, `precompute_grain`: Cinematic multi-pass post effects.

---

## 6. Design Guidelines for New Motion Projects

1. **Default to Vertical Mobile Product Simulation (V4)**: When creating social ads, app launches, or feature announcements, choose 1080x1920 vertical format with the 5-Act framework (Hook $\to$ Feed $\to$ Compose $\to$ Reaction $\to$ CTA).
2. **Always Use Super-Sampled Anti-Aliasing (SSAA)**: Never draw at native 1x resolution. Use $K=1.5$ with Lanczos downsampling for crisp, broadcast-grade vector rendering.
3. **Incorporate Authentic Mobile Gestures**: Use finger contact pads, pressure dips, expanding ripples, and modal sheets to make interfaces feel physically responsive.
4. **Synthesize Procedural Audio with Side-Chain Ducking**: Generate custom electronic soundtracks with SciPy Butterworth filters, side-chain ducking behind kick drums, and frame-accurate UI Foley clicks.
5. **Accelerate with Multi-Core Parallel Rendering**: Use `multiprocessing.Pool` with chunked pipes into `imageio-ffmpeg` to achieve 4x-8x faster render times.
