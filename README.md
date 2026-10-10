# 🎬 Procedural Motion Graphics (Python)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Antigravity Skill](https://img.shields.io/badge/Antigravity-Skill-8A2BE2.svg)](https://github.com/gnustella-lab/procedural-motion-graphics)
[![Zero Dependencies](https://img.shields.io/badge/External%20Software-None%20(Pure%20Code)-green.svg)](#)

A complete, broadcast-grade procedural motion graphics and video synthesis system written entirely in pure Python (**Pillow + NumPy + imageio-ffmpeg**).

Every frame is a deterministic mathematical function of time $t \in \mathbb{R}$. No After Effects, no Blender, no video editor, and no stock footage.

---

## 📽️ Showreel Highlights

![Showreel Preview](assets/showreel_preview.gif)

> **Output**: 1080p @ 30fps H.264 video rendered frame-by-frame directly in Python.

---

## 🌟 The Two Design Pillars

The engine provides full procedural support for two distinct broadcast design paradigms:

### 1. Flat Editorial / "Spotify Wrapped" (Recommended & Desired)
- **Aesthetic**: Saturated color-block scenes (Green, Purple, Orange, Blue, Black), crisp typography with hard offset drop shadows (`offset 8, 8`), rounded pill badges, ranked countdown charts, spinning vinyl turntables, and dynamic waveform scrubbers.
- **Physics**: Damped harmonic spring physics ($1 - e^{-kx}\cos(\omega x)$), squash & stretch ground impacts, dynamic floor contact shadows, and `smoothstep` wipes.
- **SSAA Anti-Aliasing**: Authoring in virtual coordinates, rendering at $1.5\times$ scale via `Pen`, and downsampling with Lanczos filtering for razor-sharp vector curves.
- **Compression Efficiency**: **~2.7 MB for 15s @ 720p (18x smaller!)** thanks to clean solid vector color blocks that maximize H.264 temporal inter-frame compression.

### 2. Dark Cyber Glow Compositing
- **Aesthetic**: Deep midnight navy backgrounds (`#080812`), drifting Lissajous radial gradients, and neon typography with chromatic 3D extrusions.
- **3D & Particles**: Perspective-projected 3D orbital particle clouds, Euler rotation matrices, and Painter's Algorithm depth sorting.
- **Post Pipeline**: Downsampled 4x Gaussian bloom, cut-triggered chromatic aberration spikes, and anti-banding film grain plates.

---

## 📊 File Size & Bitrate Optimization Comparison

| Metric | Version 1 (Dark Glow + Grain) | Version 2 (Flat Wrapped SSAA) |
| :--- | :--- | :--- |
| **Video File Size (15s @ 720p)** | **48.8 MB** | **2.7 MB (18x smaller!)** |
| **Visual Direction** | Cyber neon, glow, grain plates | Flat color-block, Swiss editorial |
| **Anti-Aliasing** | 1x rasterization + blur/grain mask | **SSAA 1.5x + Lanczos downsample** |
| **Motion Dynamics** | Canned cubic Bézier curves | **Damped Harmonic Spring Physics** |
| **Post-Processing Overhead** | Heavy (Bloom + CA + Grain + Vignette) | **Zero (Pristine clean vectors)** |
| **Scene Transitions** | Hard cuts + white flash + CA jump | **Concurrent Iris Wipes + Mask Slides** |

---

## 🚀 Installation & Skill Setup

### 1. Install Dependencies

```bash
pip install numpy pillow imageio imageio-ffmpeg
```

### 2. Use as an Agent Skill

#### In Google Antigravity
Clone this repository directly into your project's `.agents/skills/` directory or your global skills configuration:
```bash
git clone https://github.com/gnustella-lab/procedural-motion-graphics.git .agents/skills/procedural-motion-graphics
```

#### In Hermes Agent
```bash
git clone https://github.com/gnustella-lab/procedural-motion-graphics.git ~/.hermes/skills/procedural-motion-graphics
```

#### In Claude Code
```bash
git clone https://github.com/gnustella-lab/procedural-motion-graphics.git ~/.claude/skills/procedural-motion-graphics
```

---

## ⚡ Quickstarts

### Option A: Flat Editorial / "Wrapped" Title (Version 2 Style)

```python
import numpy as np
from PIL import Image
import imageio.v2 as imageio
from scripts.motion_engine import Pen, spring, prog

W, H, FPS = 1280, 720, 30
writer = imageio.get_writer("wrapped_title.mp4", fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p")

for frame in range(90):  # 3 seconds
    t = frame / FPS
    # 1. Super-Sampled Anti-Aliasing Canvas (1.5x Lanczos)
    pen = Pen("#1ED760", W, H, k=1.5)

    # 2. Damped Spring Physics Entrance
    p = spring(prog(t, 0.2, 1.0), k=7, w=14)
    off_x = (1.0 - p) * -1200

    # 3. Typography with Hard Offset Drop Shadow
    pen.txt(640 + off_x + 8, 360 + 8, "MOTION DESIGN", 140, (18, 18, 18))
    pen.txt(640 + off_x, 360, "MOTION DESIGN", 140, (255, 255, 255))

    # 4. Downsample to pristine 720p
    writer.append_data(np.asarray(pen.render()))

writer.close()
```

### Option B: Dark Cyber Kinetic Title (Version 1 Style)

```python
import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio
from scripts.motion_engine import ease_out_back, prog, lerp, get_font, apply_glow_bloom

W, H, FPS = 1920, 1080, 30
cx, cy = W / 2, H / 2
font = get_font(180, bold=True)

writer = imageio.get_writer("cyber_title.mp4", fps=FPS, codec="libx264", quality=9, pixelformat="yuv420p")

for frame in range(90):  # 3 seconds
    t = frame / FPS
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    q = ease_out_back(prog(t, 0.2, 1.2), s=2.0)
    y = lerp(-200, cy, q)

    # Chromatic offset extrusion
    draw.text((cx + 6, y + 6), "CYBER", font=font, fill=(255, 46, 136, 160), anchor="mm")
    draw.text((cx - 6, y - 4), "CYBER", font=font, fill=(0, 229, 255, 160), anchor="mm")
    draw.text((cx, y), "CYBER", font=font, fill=(245, 245, 250, 255), anchor="mm")

    # Composite & bloom
    img = np.array((10, 10, 18), np.float32) * (1.0 - np.asarray(layer)[..., 3:4]/255) + np.asarray(layer)[..., :3] * (np.asarray(layer)[..., 3:4]/255)
    img = apply_glow_bloom(img, threshold=80, intensity=0.5)
    writer.append_data(img.clip(0, 255).astype(np.uint8))

writer.close()
```

---

## 📁 Repository Structure

```text
procedural-motion-graphics/
├── SKILL.md                                 # Main Agentic Skill specification
├── README.md                                # Public GitHub presentation & guides
├── LICENSE                                  # MIT License
├── showreel.py                              # Master 15s showreel source
├── showreel_breakdown.txt                   # Detailed creative & technical notes
├── assets/                                  # Pre-rendered stills and animated GIF
├── scripts/                                 # Executable utilities & modular engine
│   ├── motion_engine.py                     # Reusable SSAA Pen, springs, polar morphs, & math
│   ├── render_showreel.py                   # Production CLI video renderer
│   └── preview_frame.py                     # Fast single-frame preview CLI
├── examples/                                # Standalone tutorials and recipes
│   ├── 01_quickstart_kinetic_title.py       # Kinetic typography & chromatic extrude
│   ├── 02_radial_shape_bloom.py             # Geometric polygon vertex morphing
│   ├── 03_orbital_particles_3d.py           # 3D perspective particle system
│   ├── 04_logo_stroke_reveal.py             # Trim paths vector line-draw & elastic pop
│   ├── 05_strobe_rhythmic_cuts.py           # High-energy 4-frame strobe cuts
│   └── 06_flat_wrapped_editorial.py         # Flat Wrapped editorial, springs & polar morphs
└── references/                              # In-depth technical documentation
    ├── animation-math-and-easings.md        # Damped spring physics, squash & stretch, easings
    ├── compositing-pipeline.md              # SSAA Pen, iris wipes, bitrate & H.264 optimization
    ├── creative-direction-and-pacing.md     # Flat Editorial vs Dark Cyber design pillars
    ├── polar-shape-morphing-and-ui.md       # 2D polar radius formulas & music UI components
    ├── 3d-projection-in-2d.md               # Euler rotations & perspective divide
    └── kinetic-typography-and-mattes.md     # Advance metrics & track mattes
```

---

## 📄 License

MIT License. Free for personal, commercial, and educational use.
