---
name: procedural-motion-graphics
description: >-
  Create broadcast-grade procedural motion graphics, kinetic typography, 2D/3D
  particle systems, geometric morphs, and video showreels in pure Python
  (NumPy + Pillow + imageio-ffmpeg) without external video editing software.
  Supports Native App UI / Product Simulations ("The Resume is the App"),
  Flat Editorial / "Spotify Wrapped" vector design, and Dark Cyber Glow aesthetics.
---

# Procedural Motion Graphics in Python

This skill equips agents with end-to-end expertise in generating broadcast-grade motion graphics entirely from code. Every frame is a deterministic mathematical function of time $t$, allowing 100% reproducible rendering in pure Python (Pillow + NumPy) encoded directly to H.264 via `imageio-ffmpeg`—with zero reliance on After Effects, Blender, or stock assets.

---

## 1. Quick Capabilities & Runbook

| Task | Command / Script | Reference |
| :--- | :--- | :--- |
| **App UI & Product Simulation** | `python examples/07_app_ui_product_simulation.py` | Synced lyrics, vertical app swipe, EQ bars, click ripple |
| **Flat Wrapped Editorial** | `python examples/06_flat_wrapped_editorial.py` | SSAA 1.5x, spring physics, polar morph, iris wipe |
| **Instant Frame Preview** | `python scripts/preview_frame.py --time 1.2 -o preview.png` | Fast visual debugging in 0.5s |
| **Render All Scene Stills** | `python scripts/preview_frame.py --all-scenes` | Generates 6 scene keyframes in `assets/` |
| **Render Full Showreel** | `python scripts/render_showreel.py showreel.mp4 --fps 30` | 1080p @ 30fps H.264 render |
| **Kinetic Title Quickstart** | `python examples/01_quickstart_kinetic_title.py` | 3s title sequence with bounce & bloom |
| **3D Particle Orbit** | `python examples/03_orbital_particles_3d.py` | Perspective 3D particles & depth sort |

---

## 2. The Three Design Pillars

Choose the design pillar that fits the project brief:

### Pillar 1: App UI & Native Product Simulation (V3 - Desired & Recommended)
- **Concept**: **"The Resume IS the App"**. The video recreates the interactive screens of a modern music app (Spotify/Apple Music). The viewer navigates through real UI states:
  1. **Synced Lyrics (`LETRA`)**: Karaoke-style word illumination, auto-scroll, and background color crossfading.
  2. **Playlist Tracklist (`Currículo`)**: Professional experience as tracks with animated 3-bar green equalizers on active rows.
  3. **Discography Carousel**: Horizontal album cards with dynamic count-up statistics.
  4. **Artist Profile & Micro-Interactions**: Verified artist avatar, OS mouse cursor, button click depression (8%), expanding shockwave ripple, and button state morphing (`"FOLLOW"` $\to$ `"LET'S WORK ✓"`).
- **Transitions**: Native vertical push / swipe transitions (`vertical_push_transition`).
- **Timing & Curves**: Crisp Penner cubic easings (`ease_out_cubic`, `ease_in_out_cubic`, `ease_out_back`).
- **Compression**: **Featherweight file size (~1.25 MB for 15s @ 720p — 39x smaller than V1!)** due to extreme macroblock consistency across dark UI surfaces.
- *Deep dive: [references/app-ui-and-product-simulation.md](./references/app-ui-and-product-simulation.md)*

### Pillar 2: Flat Editorial / "Spotify Wrapped" (V2)
- **Visual Style**: Saturated solid color-block scenes (Green, Purple, Orange, Blue, Black), bold typography with hard offset shadows (`+8, +8`), bouncing polar shape morphs with squash & stretch and contact shadows.
- **Physics**: Damped harmonic springs (`spring(x, k=7, w=14)`).
- **Transitions**: Concurrent circular iris wipes (`iris_wipe`).
- **Compression**: Compact file size (~2.7 MB).
- *Deep dive: [references/polar-shape-morphing-and-ui.md](./references/polar-shape-morphing-and-ui.md)*

### Pillar 3: Dark Cyber Glow Compositing (V1)
- **Visual Style**: Midnight navy backgrounds (`#080812`), Lissajous radial gradient glows, neon typography with chromatic 3D extrusions, and 3D orbital particle clouds.
- **Post Pipeline**: Downsampled Gaussian bloom pass, chromatic aberration spikes on cuts, and film grain.
- *Deep dive: [references/compositing-pipeline.md](./references/compositing-pipeline.md)*

---

## 3. Core Architecture: Super-Sampled Frame Rendering

To eliminate CPU rasterization stair-stepping, always render through `Pen` with a $1.5\times$ super-sampling factor ($K=1.5$) and Lanczos downsampling:

```python
import numpy as np
from PIL import Image
from scripts.motion_engine import Pen, ease_out_cubic, prog

W, H, FPS = 1280, 720, 30

def render_scene(t: float) -> Image.Image:
    pen = Pen("#121212", W, H, k=1.5)
    e = ease_out_cubic(prog(t, 0.2, 0.9))
    pen.txt(640, 360 + (1.0 - e) * 40, "ARTISTA VERIFICADO", 22, (30, 215, 96), anchor="mm")
    return pen.render()
```

---

## 4. Modular Toolkit (`scripts/motion_engine.py`)

### 4.1 App UI & Interactive Micro-Interactions (New in V3)
- `vertical_push_transition(curr, prev, progress)`: Mobile/desktop app vertical screen push swipe.
- `generative_cover(pen, x, y, size, seed, color)`: Algorithmic geometric album art with seeded variations.
- `mini_eq_bars(pen, x, y, t, color, count=3)`: Animated 3-bar green equalizer for active playlist tracks.
- `draw_cursor(pen, x, y, color)`: Vector OS mouse pointer arrow.
- `button_click_press(t, t_click)`: Tactile 8% button scale depression on click.
- `draw_click_ripple(pen, cx, cy, t, t_click)`: Expanding circular shockwave ripple.

### 4.2 Spring Physics & Easings
- `ease_out_cubic(x)` & `ease_in_out_cubic(x)`: Penner cubic easings for responsive UI motion.
- `ease_out_back(x, s=1.8)`: Controlled UI card/avatar pop-in overshoot.
- `spring(x, k=7, w=14)`: Damped harmonic spring oscillation.
- `smoothstep(x)`: Hermite cubic S-curve for wipes and fills.
- `squash_and_stretch(bounce)`: Deform scale $(s_x, s_y)$ on impact.

### 4.3 Vector Canvas (`Pen`)
- `Pen(bg, width, height, k=1.5)`: Manages $1.5\times$ super-sampled canvas, font loading, coordinate scaling, and Lanczos export.

### 4.4 2D Polar Shape Morphing
- `polar_radius(shape, theta)` & `morph_polar_shapes(a, b, progress)`: Continuous shape morphing across Circle, Square, Triangle, and Star without inverted topology.

### 4.5 3D Perspective Projection & Compositing
- `rotate_3d` & `project_3d`: 3D Euler rotations and perspective division.
- `apply_glow_bloom`, `apply_chromatic_aberration`, `precompute_grain`: Cinematic multi-pass post effects.

---

## 5. Design Guidelines for New Motion Projects

1. **Default to App UI / Product Simulation (V3)**: When asked to showcase a resume, portfolio, SaaS product, or music release, build it as a native interactive app session. It immediately captures attention and feels authentic.
2. **Always Use Super-Sampled Anti-Aliasing (SSAA)**: Never draw at native 1x resolution. Use `Pen(..., k=1.5)` with Lanczos downsampling for crisp, broadcast-grade vector rendering.
3. **Use Vertical Push for Screen Changes**: When transitioning between digital views, use `vertical_push_transition` to maintain mobile/desktop app realism.
4. **Enrich with Micro-Interactions**: Incorporate subtle cursor movements, click depressions, and ripple waves to bring static screens to life.
5. **Optimize Video Bitrate**: Pure UI vectors over consistent dark backgrounds (`#121212`) compress into featherweight ~1.25 MB files. Avoid heavy film grain noise.
