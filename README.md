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

## 🌟 The Three Design Pillars

The engine provides full procedural support for three distinct broadcast design paradigms:

### 1. App UI & Native Product Simulation (Version 3 - Desired & Recommended)
- **Concept**: **"The Resume IS the App"**. The video recreates the interactive screens of a modern music app (Spotify/Apple Music). The viewer navigates through real UI states:
  - **Synced Lyrics (`LETRA`)**: Karaoke-style word illumination, auto-scroll, and background color crossfading.
  - **Playlist Tracklist (`Currículo`)**: Professional experience as tracks with animated 3-bar green equalizers on active rows.
  - **Discography Carousel**: Horizontal album cards with dynamic count-up statistics.
  - **Artist Profile & Micro-Interactions**: Verified artist avatar, OS mouse cursor, button click depression (8%), expanding shockwave ripple, and button state morphing (`"FOLLOW"` $\to$ `"LET'S WORK ✓"`).
- **Transitions**: Native vertical push / swipe transitions (`vertical_push_transition`).
- **Timing & Curves**: Crisp Penner cubic easings (`ease_out_cubic`, `ease_in_out_cubic`, `ease_out_back`).
- **Compression**: **Featherweight file size (~1.25 MB for 15s @ 720p — 39x smaller than V1!)** due to extreme macroblock consistency across dark UI surfaces.

### 2. Flat Editorial / "Spotify Wrapped" (Version 2)
- **Aesthetic**: Saturated color-block scenes (Green, Purple, Orange, Blue, Black), crisp typography with hard offset drop shadows (`offset 8, 8`), rounded pill badges, ranked countdown charts, spinning vinyl turntables, and dynamic waveform scrubbers.
- **Physics**: Damped harmonic spring physics ($1 - e^{-kx}\cos(\omega x)$), squash & stretch ground impacts, dynamic floor contact shadows, and `smoothstep` wipes.
- **Compression**: **~2.7 MB for 15s @ 720p**.

### 3. Dark Cyber Glow Compositing (Version 1)
- **Aesthetic**: Deep midnight navy backgrounds (`#080812`), drifting Lissajous radial gradients, and neon typography with chromatic 3D extrusions.
- **3D & Particles**: Perspective-projected 3D orbital particle clouds, Euler rotation matrices, and Painter's Algorithm depth sorting.
- **Post Pipeline**: Downsampled 4x Gaussian bloom, cut-triggered chromatic aberration spikes, and anti-banding film grain plates.

---

## 📊 File Size & Bitrate Optimization Comparison

| Metric | Version 1 (Dark Cyber) | Version 2 (Flat Wrapped) | Version 3 (App UI Simulation) |
| :--- | :--- | :--- | :--- |
| **Video File Size (15s @ 720p)** | **48.8 MB** | **2.7 MB** | **1.25 MB (Featherweight!)** |
| **Bitrate Reduction vs. V1** | $1\times$ (Baseline) | **$18\times$ smaller** | **$39\times$ smaller** |
| **Visual Direction** | Dark neon, glow, grain | Flat color-block editorial | Native digital music player UI |
| **Anti-Aliasing** | 1x rasterization + blur/grain mask | **SSAA 1.5x + Lanczos** | **SSAA 1.5x + Lanczos** |
| **Motion Dynamics** | Canned cubic Bézier curves | Damped Harmonic Springs | **Crisp Penner UI Easings** |
| **Screen Transitions** | Hard cuts + white flash + CA jump | Concurrent Iris Wipes | **Native App Vertical Swipes** |
| **Micro-Interactions** | None | Squash & stretch impacts | **Cursor, click depression, ripples** |

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

### Option A: Native App UI Simulation (Version 3 Style)

```python
import numpy as np
from PIL import Image
import imageio.v2 as imageio
from scripts.motion_engine import Pen, ease_out_cubic, prog, mini_eq_bars

W, H, FPS = 1280, 720, 30
writer = imageio.get_writer("app_ui_preview.mp4", fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p")

for frame in range(90):  # 3 seconds
    t = frame / FPS
    pen = Pen("#121212", W, H, k=1.5)

    # Active playlist track highlight with green equalizer
    pen.rect(40, 300, 1240, 360, (31, 31, 31), r=6)
    mini_eq_bars(pen, 64, 338, t, (30, 215, 96))
    pen.txt(176, 320, "Kinetic Typography & Systems", 24, (30, 215, 96))

    writer.append_data(np.asarray(pen.render()))

writer.close()
```

### Option B: Flat Editorial / "Wrapped" Title (Version 2 Style)

```python
import numpy as np
from PIL import Image
import imageio.v2 as imageio
from scripts.motion_engine import Pen, spring, prog

W, H, FPS = 1280, 720, 30
writer = imageio.get_writer("wrapped_title.mp4", fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p")

for frame in range(90):
    t = frame / FPS
    pen = Pen("#1ED760", W, H, k=1.5)
    p = spring(prog(t, 0.2, 1.0), k=7, w=14)
    off_x = (1.0 - p) * -1200

    pen.txt(640 + off_x + 8, 360 + 8, "MOTION DESIGN", 140, (18, 18, 18))
    pen.txt(640 + off_x, 360, "MOTION DESIGN", 140, (255, 255, 255))

    writer.append_data(np.asarray(pen.render()))

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
│   ├── motion_engine.py                     # SSAA Pen, app push, covers, cursor, springs, & math
│   ├── render_showreel.py                   # Production CLI video renderer
│   └── preview_frame.py                     # Fast single-frame preview CLI
├── examples/                                # Standalone tutorials and recipes
│   ├── 01_quickstart_kinetic_title.py       # Kinetic typography & chromatic extrude
│   ├── 02_radial_shape_bloom.py             # Geometric polygon vertex morphing
│   ├── 03_orbital_particles_3d.py           # 3D perspective particle system
│   ├── 04_logo_stroke_reveal.py             # Trim paths vector line-draw & elastic pop
│   ├── 05_strobe_rhythmic_cuts.py           # High-energy 4-frame strobe cuts
│   ├── 06_flat_wrapped_editorial.py         # Flat Wrapped editorial, springs & polar morphs
│   └── 07_app_ui_product_simulation.py      # App UI simulation: synced lyrics, EQ bars, click ripple
└── references/                              # In-depth technical documentation
    ├── app-ui-and-product-simulation.md     # Synced lyrics, app push swipes, covers, micro-interactions
    ├── animation-math-and-easings.md        # Penner UI curves, spring physics, click depression
    ├── compositing-pipeline.md              # SSAA Pen, vertical app swipes, 3-way bitrate optimization
    ├── creative-direction-and-pacing.md     # The 3 Design Pillars (App UI, Wrapped, Cyber)
    ├── polar-shape-morphing-and-ui.md       # 2D polar radius formulas & music UI components
    ├── 3d-projection-in-2d.md               # Euler rotations & perspective divide
    └── kinetic-typography-and-mattes.md     # Advance metrics & track mattes
```

---

## 📄 License

MIT License. Free for personal, commercial, and educational use.
