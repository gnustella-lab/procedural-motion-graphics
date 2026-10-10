---
name: procedural-motion-graphics
description: >-
  Create broadcast-grade procedural motion graphics, kinetic typography, 2D/3D
  particle systems, geometric morphs, and video showreels in pure Python
  (NumPy + Pillow + imageio-ffmpeg) without external video editing software.
  Use this skill when asked to create or edit motion graphics, animated title
  sequences, procedural video effects, visual music visualizers, kinetic logos,
  or render deterministic frame-by-frame videos from code.
---

# Procedural Motion Graphics in Python

This skill equips agents with end-to-end expertise in generating broadcast-grade motion graphics entirely from code. Every frame is a deterministic mathematical function of time $t$, allowing 100% reproducible rendering in pure Python (Pillow + NumPy) encoded directly to H.264 via `imageio-ffmpeg`—with zero reliance on After Effects, Blender, or stock assets.

---

## 1. Quick Capabilities & Runbook

| Task | Command / Script | Reference |
| :--- | :--- | :--- |
| **Instant Frame Preview** | `python scripts/preview_frame.py --time 1.2 -o preview.png` | Fast visual debugging in 0.5s |
| **Render All Scene Stills** | `python scripts/preview_frame.py --all-scenes` | Generates 6 scene keyframes in `assets/` |
| **Render Full Showreel** | `python scripts/render_showreel.py showreel.mp4 --fps 30` | 1080p @ 30fps H.264 render |
| **Kinetic Title Quickstart** | `python examples/01_quickstart_kinetic_title.py` | 3s title sequence with bounce & bloom |
| **3D Particle Orbit** | `python examples/03_orbital_particles_3d.py` | Perspective 3D particles & depth sort |

---

## 2. Core Architecture: Frame as a Pure Function $f(t)$

Every motion graphics sequence is structured around a master timeline:
- **Resolution**: $1920 \times 1080$ (Full HD)
- **Framerate**: $30\text{ fps}$ (frame index $i \implies t = i / \text{FPS}$)
- **Determinism**: Fixed random seeds per frame (`random.seed(1000 + i)`)

```python
import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

def render_frame(i: int) -> np.ndarray:
    t = i / FPS
    # 1. Render vector shapes on transparent RGBA layer
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    # ... procedural drawing ...

    # 2. Composite over animated Lissajous background
    bg = background(t, tint)
    # 3. Post-processing: Camera -> Bloom -> Chromatic Aberration -> Grain -> Vignette
    # ...
    return final_img.clip(0, 255).astype(np.uint8)
```

---

## 3. Modular Toolkit (`scripts/motion_engine.py`)

Always leverage or import primitives from [scripts/motion_engine.py](./scripts/motion_engine.py):

### 3.1 Easing & Interpolation
- `prog(t, a, b)`: Normalized progress in $[0, 1]$.
- `ease_out_cubic(x)`: Smooth deceleration glide.
- `ease_in_out_cubic(x)`: S-curve transition.
- `ease_out_expo(x)` & `ease_in_expo(x)`: Snappy fast-in / fast-out pacing.
- `ease_out_back(x, s=1.70158)`: Overshoot spring bounce.
- `ease_out_elastic(x)`: Damped harmonic oscillation.
- `lerp(a, b, t)` / `lerpc(c1, c2, t)`: Scalar and RGB color interpolation.
*Deep dive: [references/animation-math-and-easings.md](./references/animation-math-and-easings.md)*

### 3.2 Post-Processing Compositing Pipeline
1. **Lissajous Background**: Continuous dual-radial gradient motion drifting across scene-specific tints.
2. **Bloom / Glow Pass**: Downscale 4x $\to$ Gaussian blur $\to$ threshold subtract ($\tau = 90$) $\to$ additive blend.
3. **Chromatic Aberration**: Horizontal RGB channel shift (`np.roll`), spiking up to 16px on scene cut hits.
4. **Anti-Banding Film Grain**: Precomputed Gaussian noise plates cycled per frame to prevent 8-bit H.264 banding.
5. **Vignette**: Quadratic radial edge darkening.
*Deep dive: [references/compositing-pipeline.md](./references/compositing-pipeline.md)*

### 3.3 3D Perspective Projection in 2D Canvases
- **Euler Rotations**: Rotate world coordinates $(x, y, z)$ on X, Y, and Z axes without a 3D engine.
- **Perspective Projection**: Scale $s = \frac{\text{fov}}{\text{fov} + z + z_{\text{offset}}}$, $p_x = c_x + x \cdot s$, $p_y = c_y + y \cdot s$.
- **Painter's Algorithm**: Sort points descending by $Z$ coordinate (`pts.sort(key=lambda p: -p[2])`).
- **Atmospheric Fog**: Blend particle colors toward background color based on depth.
*Deep dive: [references/3d-projection-in-2d.md](./references/3d-projection-in-2d.md)*

### 3.4 Kinetic Typography & Track Mattes
- **Advance Width Tracking**: Accurate baseline positioning using `textbbox` and `textlength`.
- **Chromatic 3D Extrusion**: Layered pink and cyan offset shadows behind hero text.
- **Luminance Track Mattes**: Text reveals via `ImageChops.multiply` on luminance layers.
*Deep dive: [references/kinetic-typography-and-mattes.md](./references/kinetic-typography-and-mattes.md)*

---

## 4. Design Guidelines for New Motion Projects

1. **Avoid Linear Motion**: Every moving element must use an easing curve (`ease_out_back` for entrances, `ease_in_expo` for exits).
2. **Use Staggering**: Offset elements radially or sequentially by $50\text{ms}-100\text{ms}$. Never let a multi-element layout arrive simultaneously.
3. **High-Contrast Palette**: Use deep midnight navy backgrounds (`#0A0A12`) so neon accents (Pink `#FF2E88`, Cyan `#00E5FF`, Yellow `#FFD600`, Violet `#7C4DFF`) glow vibrantly through the bloom pass.
4. **Energy Pacing**: Build an emotional arc (Ignition $\to$ Rhythm $\to$ Kinetic Message $\to$ 3D Depth $\to$ Climax Cuts $\to$ Brand Resolve). See [references/creative-direction-and-pacing.md](./references/creative-direction-and-pacing.md).
5. **Test Fast with Single-Frame Previews**: When prototyping, render individual frames using `scripts/preview_frame.py` rather than waiting for multi-minute video encodings.
