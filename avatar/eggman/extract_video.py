#!/usr/bin/env python3
"""Extract Eggman's filmed pixels, remove the monitor background, and export sheets."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent


def screen_matte(rgb):
    """Estimate the smooth screen color from the crop border, retaining ink and fill."""
    values = np.asarray(rgb, dtype=np.float64)
    h, w = values.shape[:2]
    y, x = np.mgrid[-1:1:complex(h), -1:1:complex(w)]
    design = np.stack([np.ones_like(x), x, y, x*x, x*y, y*y], axis=-1)
    border = (np.abs(x) > .92) | (np.abs(y) > .92)
    # Red has the greatest separation between the blue monitor and the egg.
    coefficients = np.linalg.lstsq(design[border], values[:, :, 0][border], rcond=None)[0]
    difference = values[:, :, 0] - design @ coefficients
    ink = Image.fromarray(np.uint8(difference < -14)*255)
    # Close tiny compression breaks in the outline, then classify enclosed
    # regions. This retains the complete body and shoes even where the filmed
    # screen shading makes their fill close to the background color.
    regions = ink.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    ImageDraw.floodfill(regions, (0, 0), 128)
    matte = np.asarray(regions) == 255
    while True:
        unclassified = np.asarray(regions) == 0
        if not unclassified.any():
            break
        sy, sx = np.argwhere(unclassified)[0]
        ImageDraw.floodfill(regions, (int(sx), int(sy)), 64)
        region = np.asarray(regions) == 64
        # Background openings between arms/legs remain transparent. The
        # light body, eyes, and shoes retain their original source pixels.
        if np.median(difference[region]) > 8:
            matte |= region
        regions.paste(128, mask=Image.fromarray(np.uint8(region)*255))
    return Image.fromarray(np.uint8(matte)*255)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--source-start', type=float, default=0)
    parser.add_argument('--output', type=Path, default=HERE)
    parser.add_argument('--spec', type=Path, default=HERE/'source-clips.json',
                        help='Source manifest; use a separate one for unassigned candidates')
    parser.add_argument('--preview', action='store_true', help='Export RGB565 GIF previews beside the sheets')
    parser.add_argument('--clip', action='append')
    parser.add_argument('--qa', type=Path, help='Save full-size source crops and transparent cutouts')
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text())
    clips = [c for c in spec['clips'] if not args.clip or c['name'] in args.clip]
    if not clips or (args.clip and set(args.clip)-{c['name'] for c in clips}):
        parser.error('Unknown clip name')
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'stream=width,height:format=duration', '-of', 'json', str(args.video)]))
    stream = probe['streams'][0]
    if [stream['width'], stream['height']] != spec['source_resolution']:
        parser.error('The recorded crops require a 1920x1080 source')
    for clip in clips:
        start = clip['start']-args.source_start
        if start < 0 or start + clip['frames']/spec['fps'] > float(probe['format']['duration']):
            parser.error('Input does not contain the complete requested sequence')
    args.output.mkdir(parents=True, exist_ok=True)
    for clip in clips:
        x, y, w, h = clip['crop']
        cols = spec['columns']
        sheet = Image.new('RGB', (64*cols, 64*((clip['frames']+cols-1)//cols)))
        with tempfile.TemporaryDirectory(prefix='eggman-') as tmp:
            subprocess.run([
                'ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(clip['start']-args.source_start),
                '-i', str(args.video), '-vf', f"fps={spec['fps']},crop={w}:{h}:{x}:{y}",
                '-frames:v', str(clip['frames']), str(Path(tmp)/'%03d.png')], check=True)
            for i in range(clip['frames']):
                rgb = Image.open(Path(tmp)/f'{i+1:03d}.png').convert('RGB')
                alpha = screen_matte(rgb)
                rgba = rgb.copy().convert('RGBA')
                rgba.putalpha(alpha)
                if args.qa:
                    dest = args.qa/clip['name']
                    dest.mkdir(parents=True, exist_ok=True)
                    rgb.save(dest/f'{i:02d}-source.png')
                    rgba.save(dest/f'{i:02d}-cutout.png')
                black = Image.new('RGB', rgb.size)
                black.paste(rgb, mask=alpha)
                tile = Image.new('RGB', (64,64))
                tile.paste(black.resize(clip['size'], Image.Resampling.LANCZOS), tuple(clip['pos']))
                sheet.paste(tile, (i%cols*64, i//cols*64))
        sheet.save(args.output/f"video-{clip['name']}.png")
        if args.preview:
            # Match the firmware's RGB565 conversion and 15 fps sample timing.
            rgb = np.asarray(sheet).astype(np.uint16)
            rgb[:, :, 0] = (rgb[:, :, 0] >> 3)*255//31
            rgb[:, :, 1] = (rgb[:, :, 1] >> 2)*255//63
            rgb[:, :, 2] = (rgb[:, :, 2] >> 3)*255//31
            preview = Image.fromarray(rgb.astype(np.uint8))
            palette = preview.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                                       dither=Image.Dither.NONE)
            frames = []
            for i in range(clip['frames']):
                x, y = i%cols*64, i//cols*64
                frame = preview.crop((x,y,x+64,y+64)).resize((256,256), Image.Resampling.NEAREST)
                frames.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))
            durations = [(round((i+1)*100/spec['fps'])-round(i*100/spec['fps']))*10
                         for i in range(clip['frames'])]
            frames[0].save(args.output/f"{clip['name']}.gif", save_all=True,
                           append_images=frames[1:], duration=durations, loop=0)
        print(f"{clip['name']}: {clip['frames']} source samples at {spec['fps']} fps")


if __name__ == '__main__':
    main()
