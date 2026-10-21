#!/usr/bin/env python3
"""Losslessly pack recorded Eggman RGB565 samples with pixel LZ runs."""
import json
from pathlib import Path
import sys
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from sprite_codec import write_sprites



def main():
    spec = json.loads((HERE/'source-clips.json').read_text())
    frames, sequences = [], []
    for clip in spec['clips']:
        sequences.append((clip['name'].upper().replace('-', '_'), len(frames), clip['frames']))
        sheet = Image.open(HERE/f"video-{clip['name']}.png").convert('RGB')
        columns = spec['columns']
        expected = (64*columns, 64*((clip['frames']+columns-1)//columns))
        if sheet.size != expected:
            raise ValueError(f"Unexpected sheet size for {clip['name']}: {sheet.size}")
        for i in range(clip['frames']):
            x, y = i%columns*64, i//columns*64
            tile = sheet.crop((x,y,x+64,y+64))
            frames.append([((r>>3)<<11) | ((g>>2)<<5) | (b>>3)
                           for r,g,b in tile.get_flattened_data()])
    flash_bytes = write_sprites(HERE/'sprites.h', frames, sequences, 'EGGMAN')
    (HERE/'asset-info.json').write_text(json.dumps({
        'character':'Eggman', 'reference':spec['source'], 'format':'RGB565 pixel LZ (lossless)',
        'frame_size':spec['frame_size'], 'frames':len(frames), 'flash_bytes':flash_bytes,
        'uncompressed_bytes':len(frames)*8192,
        'generator':'Source-video frames via FFmpeg; outline and screen-color mattes via Pillow/NumPy',
        'provenance':'source-clips.json'
    },indent=2)+'\n')
    print(f'Packed {len(frames)} frames; {flash_bytes} bytes including offsets (lossless).')


if __name__ == '__main__':
    main()
