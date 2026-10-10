#!/usr/bin/env python3
"""Standalone production renderer for the Procedural Motion Graphics Showreel.

Usage:
    python scripts/render_showreel.py [output.mp4] [--fps 30] [--quality 9]
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import showreel
import imageio.v2 as imageio

def main():
    parser = argparse.ArgumentParser(description="Render the procedural motion graphics showreel.")
    parser.add_argument("output", nargs="?", default="showreel.mp4", help="Output MP4 file path (default: showreel.mp4)")
    parser.add_argument("--fps", type=int, default=showreel.FPS, help="Frames per second (default: 30)")
    parser.add_argument("--quality", type=int, default=9, help="H.264 quality level 1-10 (default: 9)")
    parser.add_argument("--start", type=float, default=0.0, help="Start time in seconds (default: 0.0)")
    parser.add_argument("--end", type=float, default=showreel.DUR, help="End time in seconds (default: 15.0)")
    args = parser.parse_args()

    start_frame = int(args.start * args.fps)
    end_frame = int(args.end * args.fps)
    total_frames = end_frame - start_frame

    print(f"=======================================================")
    print(f" Rendering Procedural Showreel: {args.output}")
    print(f" Resolution: {showreel.W}x{showreel.H} | FPS: {args.fps}")
    print(f" Frames: {start_frame} to {end_frame} ({total_frames} total frames)")
    print(f"=======================================================")

    t0 = time.time()
    writer = imageio.get_writer(
        args.output,
        fps=args.fps,
        codec="libx264",
        quality=args.quality,
        pixelformat="yuv420p",
        macro_block_size=8
    )

    for i in range(start_frame, end_frame):
        showreel.random.seed(1000 + i)
        frame_data = showreel.frame(i)
        writer.append_data(frame_data)
        if (i - start_frame + 1) % 30 == 0 or (i - start_frame + 1) == total_frames:
            elapsed = time.time() - t0
            fps_speed = (i - start_frame + 1) / max(0.001, elapsed)
            remaining = (total_frames - (i - start_frame + 1)) / max(0.001, fps_speed)
            print(f"  Frame {i - start_frame + 1}/{total_frames} ({((i - start_frame + 1)/total_frames)*100:.1f}%) | Speed: {fps_speed:.2f} fps | ETA: {remaining:.1f}s", flush=True)

    writer.close()
    elapsed = time.time() - t0
    print(f"\nRender completed in {elapsed:.2f} seconds.")
    print(f"Output saved to: {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()
