#!/usr/bin/env python3
"""Package Oyster's approved video dance sheets as RGB565."""
from pathlib import Path
import json
import sys
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from sprite_codec import write_sprites
frames = []
offsets = []
for name, filename, columns, rows, count in (("IDLE", "video-headbang.png", 8, 1, 8),
                                            ("LISTENING", "video-arms-back.png", 8, 2, 10),
                                            ("FRONT", "video-greeting.png", 8, 1, 8),
                                            ("PRINTOUT", "video-printout.png", 7, 4, 28)):
    offsets.append((name, len(frames), count))
    source = Image.open(HERE / filename).convert("RGB")
    for i in range(count):
        x, y = i % columns, i // columns
        box = (round(x * source.width / columns), round(y * source.height / rows),
               round((x + 1) * source.width / columns), round((y + 1) * source.height / rows))
        sprite = source.crop(box).resize((64, 64), Image.Resampling.LANCZOS)
        frames.append([((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                       for r, g, b in sprite.get_flattened_data()])
flash_bytes = write_sprites(HERE/"sprites.h", frames, offsets, "OYSTER")
(HERE / "asset-info.json").write_text(json.dumps({
    "character": "Oyster", "reference": "https://www.youtube.com/watch?v=a8K6QUPmv8Q",
    "generator": "Source-video frames via FFmpeg; recorded mattes via Pillow", "format": "RGB565 pixel LZ (lossless)", "frame_size": [64, 64],
    "frames": len(frames), "flash_bytes": flash_bytes, "uncompressed_bytes": len(frames)*64*64*2,
    "provenance": "source-clips.json"
}, indent=2) + "\n")
print(f"Packed {len(frames)} frames; {flash_bytes} bytes of read-only sprite data.")
