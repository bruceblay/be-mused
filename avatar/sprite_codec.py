"""Lossless sprite storage shared by the source-video packers."""
from collections import Counter, defaultdict


def compress(frame, palette_indices, previous_frame=None):
    """Byte commands: top two bits are literal (0), copy (1), or skip (2).
    Low six bits encode count-1; 63 means a following uint16 count. Copies
    add a uint16 distance; literal bytes index the shared RGB565 palette,
    with 255 escaping a raw uint16 pixel. Words are little-endian.
    Copies refer to already decoded current-frame pixels and may overlap.
    """
    out, literals = bytearray(), []
    positions = defaultdict(list)

    def word(value):
        out.extend(value.to_bytes(2, 'little'))

    def command(kind, count):
        out.append(kind | min(count-1, 63))
        if count >= 64:
            word(count)

    def flush():
        if literals:
            command(0, len(literals))
            for value in literals:
                index = palette_indices.get(value, 255)
                out.append(index)
                if index == 255:
                    word(value)
            literals.clear()

    i = 0
    while i < len(frame):
        skip = 0
        if previous_frame is not None:
            while i+skip < len(frame) and frame[i+skip] == previous_frame[i+skip]:
                skip += 1
        best_length, best_distance = 0, 0
        if skip < 2:
            for start in reversed(positions[tuple(frame[i:i+3])][-32:]):
                length = 0
                while i+length < len(frame) and frame[start+length] == frame[i+length]:
                    length += 1
                if length > best_length:
                    best_length, best_distance = length, i-start
                if length == len(frame)-i:
                    break
        if skip >= 2:
            flush()
            command(0x80, skip)
            advance = skip
        elif best_length >= 3:
            flush()
            command(0x40, best_length)
            word(best_distance)
            advance = best_length
        else:
            literals.append(frame[i])
            advance = 1
        for j in range(i, i+advance):
            positions[tuple(frame[j:j+3])].append(j)
        i += advance
    flush()
    return out


def write_sprites(path, frames, sequences, prefix):
    symbol = prefix.lower()
    palette = [value for value, _ in Counter(v for frame in frames for v in frame).most_common(255)]
    palette_indices = {value: i for i, value in enumerate(palette)}
    data, offsets, keyframes = bytearray(), [0], []
    starts = {first for _, first, _ in sequences}
    keyframe = 0
    for i, frame in enumerate(frames):
        independent = compress(frame, palette_indices)
        delta = compress(frame, palette_indices, frames[i-1]) if i not in starts else independent
        if i in starts or len(independent) <= len(delta):
            encoded, keyframe = independent, i
        else:
            encoded = delta
        data.extend(encoded)
        offsets.append(len(data))
        keyframes.append(keyframe)
    with path.open('w') as out:
        out.write('/* Lossless RGB565 pixel LZ. Source pixels and cadence: source-clips.json. */\n')
        for name, first, count in sequences:
            out.write(f'enum {{ {prefix}_{name}_FIRST = {first}, {prefix}_{name}_COUNT = {count} }};\n')
        out.write(f'enum {{ {prefix}_FRAME_COUNT = {len(frames)} }};\n')
        out.write(f'static const uint16_t {symbol}_palette[] = {{'+','.join(f'0x{v:04x}' for v in palette)+'};\n')
        out.write(f'static const uint32_t {symbol}_offsets[] = {{\n'+','.join(map(str,offsets))+'\n};\n')
        out.write(f'static const uint8_t {symbol}_keyframes[] = {{'+','.join(map(str,keyframes))+'};\n')
        out.write(f'static const uint8_t {symbol}_data[{len(data)}] = {{\n')
        for i in range(0,len(data),32):
            out.write(','.join(f'0x{v:02x}' for v in data[i:i+32])+',\n')
        out.write('};\n')
        # Independent uncompressed source pixels for host verification only.
        out.write(f'#ifdef {prefix}_VERIFY_RAW\n')
        out.write(f'static const uint16_t {symbol}_sprites[{len(frames)}][4096] = {{\n')
        for frame in frames:
            out.write('{\n')
            for i in range(0,len(frame),32):
                out.write(','.join(f'0x{v:04x}' for v in frame[i:i+32])+',\n')
            out.write('},\n')
        out.write('};\n#endif\n')
    return len(data)+len(offsets)*4+len(keyframes)+len(palette)*2
