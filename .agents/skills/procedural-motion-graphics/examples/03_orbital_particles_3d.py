"""Example 03: 3D Orbital Particle System with Depth Sorting.
Demonstrates 3D perspective projection, Euler rotation matrices,
painter's algorithm depth sorting, and atmospheric depth fading.
"""

import sys, os, math
import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.motion_engine import (
    ease_out_expo, ease_in_expo, prog, clamp, lerpc,
    rotate_3d, project_3d, apply_glow_bloom, precompute_vignette
)

W, H, FPS, DUR = 1920, 1080, 30, 3.0
N = int(FPS * DUR)
cx, cy = W / 2, H / 2

BG = (10, 10, 18)
PAL = [(255, 46, 136), (0, 229, 255), (124, 77, 255)]
vignette = precompute_vignette(W, H)

def render_frame(frame_idx):
    t = frame_idx / FPS
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    intro = ease_out_expo(prog(t, 0.0, 0.8))
    outro = ease_in_expo(prog(t, 2.3, 2.9))

    pts3 = []
    for ring in range(3):
        count = 60
        radius = 380 + ring * 90
        tilt = 0.9 + ring * 0.35 + t * 0.3

        for i in range(count):
            ang = i / count * 2.0 * math.pi + t * (1.2 - ring * 0.3)
            # Base ring coords in XZ plane
            x, y, z = radius * math.cos(ang), 0.0, radius * math.sin(ang)

            # Apply tilt around X, then spin around Y
            x, y, z = rotate_3d(x, y, z, rx=tilt, ry=t * 0.8 + ring)
            pts3.append((x, y, z, PAL[ring % len(PAL)]))

    # Painter's Algorithm: Sort by depth (farthest first)
    pts3.sort(key=lambda p: -p[2])

    for x, y, z, col in pts3:
        px, py, s = project_3d(x, y, z, cx, cy, fov=900.0, z_offset=600.0)
        s = s * intro * (1.0 - outro) * 1.6
        r = max(1.0, 9.0 * s)
        depth = clamp(1.0 - (z + 500.0) / 1000.0)
        # Atmospheric depth color blend
        c_depth = lerpc(BG, col, 0.35 + 0.65 * depth)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=c_depth)

    bg = np.array(BG, np.float32)
    rgb = np.asarray(layer, np.float32)
    alpha = rgb[..., 3:4] / 255.0
    img = bg * (1.0 - alpha) + rgb[..., :3] * alpha
    img = apply_glow_bloom(img, threshold=80, intensity=0.6)
    img = img * vignette
    return img.clip(0, 255).astype(np.uint8)

if __name__ == "__main__":
    out_file = "examples_output_orbit.mp4"
    print(f"Rendering {N} frames to {out_file}...")
    writer = imageio.get_writer(out_file, fps=FPS, codec="libx264", quality=9, pixelformat="yuv420p")
    for i in range(N):
        writer.append_data(render_frame(i))
    writer.close()
    print("Done:", out_file)
