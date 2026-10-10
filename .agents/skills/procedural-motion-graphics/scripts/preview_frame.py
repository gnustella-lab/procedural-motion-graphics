#!/usr/bin/env python3
"""CLI utility to preview individual frames or scene stills instantly without rendering the full video.

Usage:
    python scripts/preview_frame.py --time 1.2 --output preview.png
    python scripts/preview_frame.py --frame 45 --scale 0.5
    python scripts/preview_frame.py --all-scenes --output-dir assets/
"""

import argparse
import os
import sys
from PIL import Image

# Add root folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import showreel

def main():
    parser = argparse.ArgumentParser(description="Render single frames or scene previews.")
    parser.add_argument("--time", "-t", type=float, help="Timestamp in seconds to render (0.0 to 15.0)")
    parser.add_argument("--frame", "-f", type=int, help="Frame index to render (0 to 449)")
    parser.add_argument("--output", "-o", default="preview.png", help="Output file path (default: preview.png)")
    parser.add_argument("--scale", "-s", type=float, default=1.0, help="Resolution scale factor (e.g. 0.5 for 960x540)")
    parser.add_argument("--all-scenes", action="store_true", help="Render representative still for each of the 6 scenes")
    parser.add_argument("--output-dir", default="assets", help="Directory for scene stills (default: assets)")
    args = parser.parse_args()

    if args.all_scenes:
        os.makedirs(args.output_dir, exist_ok=True)
        scenes = [
            (1.2, "scene1_ignition.png"),
            (3.5, "scene2_grid.png"),
            (6.2, "scene3_type.png"),
            (9.5, "scene4_orbit.png"),
            (12.0, "scene5_cuts.png"),
            (14.2, "scene6_logo.png"),
        ]
        print(f"Rendering all 6 scene stills into {args.output_dir}/ ...")
        for t, filename in scenes:
            frame_idx = int(t * showreel.FPS)
            arr = showreel.frame(frame_idx)
            img = Image.fromarray(arr)
            if args.scale != 1.0:
                img = img.resize((int(img.width * args.scale), int(img.height * args.scale)), Image.LANCZOS)
            dest = os.path.join(args.output_dir, filename)
            img.save(dest, optimize=True)
            print(f"  -> {dest} (t={t:.1f}s, frame={frame_idx})")
        print("Done rendering scenes.")
        return

    # Single frame render
    if args.frame is not None:
        frame_idx = args.frame
    elif args.time is not None:
        frame_idx = int(args.time * showreel.FPS)
    else:
        frame_idx = 0

    frame_idx = max(0, min(showreel.N - 1, frame_idx))
    t = frame_idx / showreel.FPS
    print(f"Rendering frame {frame_idx} (t={t:.2f}s)...")
    arr = showreel.frame(frame_idx)
    img = Image.fromarray(arr)
    if args.scale != 1.0:
        img = img.resize((int(img.width * args.scale), int(img.height * args.scale)), Image.LANCZOS)
    img.save(args.output, optimize=True)
    print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()
