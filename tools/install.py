#!/usr/bin/env python3
"""Install the character pack into an existing Muse Gadget SDK checkout."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
REVISION = '812c46f9fe42b69d916613a9dc702cbac5ff7b54'
RUNTIME = ['muse_pixel.c', 'characters.h', 'muse_default.c', 'muse_default.h'] + [
    f'{name}/sprites.h' for name in ('tayne', 'celery-man', 'oyster', 'eggman')
]


def install(sdk, check=False):
    sdk = sdk.resolve()
    component = sdk / 'esp32/components/muse'
    if not (component / 'muse_pixel.h').is_file():
        raise RuntimeError('Pass the Muse Gadget SDK repository root (the directory containing esp32).')
    git = ['git', '-C', str(sdk)]
    revision = subprocess.check_output(git + ['rev-parse', 'HEAD'], text=True).strip()
    if revision != REVISION:
        raise RuntimeError(f'Use the supported SDK revision {REVISION}; found {revision}. See INSTALL.md#update for migration instructions.')
    patch = str(ROOT / 'patches/muse-character-menu.patch')
    def applicable(reverse=False, path=patch):
        args = git + ['apply', '--check'] + (['--reverse'] if reverse else []) + [path]
        return subprocess.run(args, capture_output=True).returncode == 0
    applied = applicable(reverse=True)
    if not applied and not applicable():
        raise RuntimeError('The SDK menu/build files conflict with the patch; no files were changed.')
    timing_patch = str(ROOT / 'patches/muse-character-timing.patch')
    timing_applied = applicable(reverse=True, path=timing_patch)
    if not timing_applied and not applicable(path=timing_patch):
        raise RuntimeError('The SDK startup/shutdown files conflict with the timing patch; no files were changed.')
    integration = ['esp32/components/muse/CMakeLists.txt', 'esp32/components/muse/muse_menu.c',
                   'esp32/components/muse/muse_settings_ui.c', 'esp32/components/muse/muse_app.c',
                   'esp32/components/muse/muse_input.c']
    previous_hashes = [json.loads((ROOT/'patches'/name).read_text()) for name in
                       ('v3-runtime-sha256.json', 'v4-runtime-sha256.json', 'v5-runtime-sha256.json', 'v6-runtime-sha256.json', 'v7-runtime-sha256.json', 'v8-runtime-sha256.json', 'v9-runtime-sha256.json', 'v10-runtime-sha256.json', 'v11-runtime-sha256.json', 'v12-runtime-sha256.json')]
    avatar = component / 'avatar'
    if avatar.is_symlink() or any((avatar / f).is_symlink() for f in RUNTIME):
        raise RuntimeError('Refusing to install through an avatar symlink.')
    for name in RUNTIME:
        source, target = ROOT / 'avatar' / name, avatar / name
        if target.parent.is_symlink():
            raise RuntimeError(f'Refusing to install through symlink: {target.parent}')
        known_old = False
        if target.is_file():
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            known_old = applied and any(digest == hashes.get(name) for hashes in previous_hashes)
        if target.exists() and not known_old and (not target.is_file() or target.read_bytes() != source.read_bytes()):
            raise RuntimeError(f'Existing custom avatar file differs: {target}. Back it up separately before installing.')
    if check:
        print('Compatible. Menu patch ' + ('already applied.' if applied else 'ready to apply.'))
        print('Timing patch ' + ('already applied.' if timing_applied else 'ready to apply.'))
        return
    touched = [sdk/name for name in integration] + [avatar/name for name in RUNTIME]
    previous = {p: p.read_bytes() if p.exists() else None for p in touched}
    try:
        if not applied:
            subprocess.run(git + ['apply', patch], check=True)
        if not timing_applied:
            subprocess.run(git + ['apply', timing_patch], check=True)
        for name in RUNTIME:
            target = avatar / name
            if not target.exists() or target.read_bytes() != (ROOT/'avatar'/name).read_bytes():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / 'avatar' / name, target)
    except Exception:
        for target, data in previous.items():
            if data is None: target.unlink(missing_ok=True)
            else: target.write_bytes(data)
        raise
    print(f'Installed Tayne, Celery Man, Oyster, Eggman and the default-pet integration into {avatar}')
    print('Next: choose your board and follow INSTALL.md to configure and build.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sdk', type=Path, help='Path to the muse-gadget-sdk repository')
    parser.add_argument('--check', action='store_true', help='Check compatibility without writing')
    args = parser.parse_args()
    try:
        install(args.sdk, args.check)
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
