---
name: procedural-motion-graphics
description: >-
  Create broadcast-grade procedural motion graphics, kinetic typography, 2D/3D
  particle systems, geometric morphs, and video showreels in pure Python
  (NumPy + Pillow + imageio-ffmpeg) without external video editing software.
  Supports both Flat Editorial / "Spotify Wrapped" vector design and Dark Cyber
  Glow aesthetics with spring physics, SSAA anti-aliasing, and pure code rendering.
---

# Procedural Motion Graphics in Python

This skill equips agents with end-to-end expertise in generating broadcast-grade motion graphics entirely from code. Every frame is a deterministic mathematical function of time $t$, allowing 100% reproducible rendering in pure Python (Pillow + NumPy) encoded directly to H.264 via `imageio-ffmpeg`—with zero reliance on After Effects, Blender, or stock assets.

---

## 1. Quick Capabilities & Runbook

| Task | Command / Script | Reference |
| :--- | :--- | :--- |
| **Flat Wrapped Editorial** | `python examples/06_flat_wrapped_editorial.py` | SSAA 1.5x, spring physics, polar morph, iris wipe |
| **Instant Frame Preview** | `python scripts/preview_frame.py --time 1.2 -o preview.png` | Fast visual debugging in 0.5s |
| **Render All Scene Stills** | `python scripts/preview_frame.py --all-scenes` | Generates 6 scene keyframes in `assets/` |
| **Render Full Showreel** | `python scripts/render_showreel.py showreel.mp4 --fps 30` | 1080p @ 30fps H.264 render |
| **Kinetic Title Quickstart** | `python examples/01_quickstart_kinetic_title.py` | 3s title sequence with bounce & bloom |
| **3D Particle Orbit** | `python examples/03_orbital_particles_3d.py` | Perspective 3D particles & depth sort |
| **Trim Path Logo Reveal** | `python examples/04_logo_stroke_reveal.py` | Vector line-draw & elastic core pop |

---

## 2. The Two Design Pillars

Choose the design pillar that fits the project brief:

### Pillar 1: Flat Editorial / "Spotify Wrapped" (Recommended & Desired)
- **Visual Style**: Bold, saturated solid color-block backgrounds per scene (Green `#1ED760`, Purple `#8B3DFF`, Orange `#FF6437`, Blue `#2D46B9`, Black `#121212`). Pure vector forms, hard offset drop shadows (`offset 8, 8`), rounded pill badges, ranked countdown charts, spinning vinyl turntables, and dynamic waveform scrubbers.
- **Physics**: Damped harmonic spring physics (`spring(x, k=7, w=14)`), squash & stretch impacts, dynamic floor contact shadows, and `smoothstep` wipes.
- **Anti-Aliasing (SSAA)**: Draw onto virtual $1.5\times$ canvas via `Pen` and downsample to native resolution via Lanczos filtering.
- **Post-Processing**: **Zero noise/bloom/grain**.
- **Compression**: **Ultra-compact file size (~2.7 MB vs 48 MB)** because solid color blocks compress with extreme temporal efficiency.
- *Deep dive: [references/polar-shape-morphing-and-ui.md](./references/polar-shape-morphing-and-ui.md)*

### Pillar 2: Dark Cyber Glow Compositing
- **Visual Style**: Midnight navy backgrounds (`#080812`), Lissajous radial gradient glows, neon typography with chromatic 3D extrusions, and 3D orbital particle clouds.
- **Post-Processing**: Downsampled Gaussian bloom pass, chromatic aberration spikes on cuts, film grain dithering, and quadratic vignette.
- *Deep dive: [references/compositing-pipeline.md](./references/compositing-pipeline.md)*

---

## 3. Core Architecture: Super-Sampled Frame Rendering

To eliminate CPU rasterization stair-stepping, always render through `Pen` with a $1.5\times$ super-sampling factor ($K=1.5$):

```python
import numpy as np
from PIL import Image
from scripts.motion_engine import Pen, spring, smoothstep, prog, iris_wipe

W, H, FPS = 1280, 720, 30

def render_scene(t: float) -> Image.Image:
    # 1. Initialize SSAA canvas with scene background color
    pen = Pen("#1ED760", W, H, k=1.5)
    
    # 2. Animate elements with damped spring physics
    p = spring(prog(t, 0.2, 1.0), k=7, w=14)
    offset_x = (1.0 - p) * -1200
    
    # Hard offset drop shadow + hero text
    pen.txt(640 + offset_x + 8, 360 + 8, "MOTION DESIGN", 140, (18, 18, 18))
    pen.txt(640 + offset_x, 360, "MOTION DESIGN", 140, (255, 255, 255))
    
    # 3. Downsample with Lanczos to eliminate all aliasing
    return pen.render()
```

---

## 4. Modular Toolkit (`scripts/motion_engine.py`)

Always leverage primitives from [scripts/motion_engine.py](./scripts/motion_engine.py):

### 4.1 Spring Physics & Easings
- `spring(x, k=7, w=14)`: Damped harmonic oscillation ($1 - e^{-kx}\cos(\omega x)$). Tactile overshoot and settling.
- `smoothstep(x)`: Hermite cubic S-curve ($3x^2 - 2x^3$) for linear wipes and progress bars.
- `squash_and_stretch(bounce)`: Calculate $(s_x, s_y)$ scale deformation factors for ground bounces.
- `contact_shadow_scale(bounce)`: Reactive shadow sizing and opacity tied to object elevation.
- `ease_out_back(x, s=1.70158)`: Canned overshoot curve.
- `lerp(a, b, t)` / `lerpc(c1, c2, t)`: Scalar and RGB color interpolation.
*Deep dive: [references/animation-math-and-easings.md](./references/animation-math-and-easings.md)*

### 4.2 Vector Drawing & Super-Sampling (`Pen`)
- `Pen(bg, width, height, k=1.5)`: Manages super-sampling canvas, font loading, coordinate scaling, and Lanczos export.
- `pen.rect(x0, y0, x1, y1, fill, r=0)`: Sharp or rounded rectangles.
- `pen.ell(cx, cy, r, fill, outline, width)`: Antialiased circles and ellipses.
- `pen.poly(pts, fill)`: Arbitrary polygon drawing.
- `pen.txt(x, y, s, size, fill, anchor, bold)`: Scaled typography.
- `pen.tw(s, size, bold)`: Text advance width measurement in unscaled coordinates.

### 4.3 2D Polar Shape Morphing
- `polar_radius(shape, theta)`: Analytical radial profile for Circle (0), Square (1), Triangle (2), and Star (3).
- `morph_polar_shapes(a, b, progress, num_samples=72)`: Continuous vertex interpolation without topology inversion.
- `polar_to_cartesian(cx, cy, pts, scale, scale_x, scale_y)`: Conversion to Cartesian space with squash & stretch.
*Deep dive: [references/polar-shape-morphing-and-ui.md](./references/polar-shape-morphing-and-ui.md)*

### 4.4 Scene Transitions
- `iris_wipe(img_curr, img_prev, progress)`: Continuous circular mask reveal where the outgoing scene remains actively animating.
- Sliding mask reveals: Stencil boxes sliding away to uncover headlines.

### 4.5 3D Perspective Projection & Compositing
- `rotate_3d` & `project_3d`: 3D Euler rotations and perspective division for particle clouds.
- `apply_glow_bloom`: Downsampled 4x Gaussian bloom pass for dark emissive styles.
- `apply_chromatic_aberration`: RGB channel horizontal shift on cuts.
- `precompute_grain`: Cyclic Gaussian noise plates to prevent 8-bit gradient banding.

---

## 5. Design Guidelines for New Motion Projects

1. **Prioritize the Flat Editorial / "Wrapped" Aesthetic (V2)**: Unless dark cyber neon is explicitly requested, default to flat, bold, saturated color-block styling. It delivers higher editorial punch and renders 18x smaller video files.
2. **Never Draw at 1x Native Resolution**: Always use `Pen(..., k=1.5)` with Lanczos downsampling to ensure smooth, professional vector outlines.
3. **Use Spring Physics for Entrances**: Replace static Bézier easings with `spring(prog(t, a, b))` for physical weight and lively settling.
4. **Preserve Pacing with Stagger**: Offset consecutive list items or letters by $50\text{ms}-100\text{ms}$. Never allow multiple elements to land simultaneously.
5. **Keep Video Files Efficient**: Avoid gratuitous procedural film grain on flat graphics; solid color areas enable H.264 temporal compression to achieve pristine quality at ~2-3 MB.
6. **Test Fast with Single-Frame Previews**: Use `python scripts/preview_frame.py --time <t> -o preview.png` for instant sub-second feedback during development.
