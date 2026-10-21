from pathlib import Path
import sys
import os
import subprocess
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from boards import BOARDS
from build import command

SDK = Path(os.environ.get("MUSE_TEST_SDK", Path(__file__).resolve().parents[2]/"muse-gadget-sdk"))


class BoardTests(unittest.TestCase):
    @unittest.skipUnless((SDK/'esp32/components/muse/muse_ui.c').exists(), 'Set MUSE_TEST_SDK')
    def test_upstream_avatar_layout(self):
        source = (SDK/'esp32/components/muse/muse_ui.c').read_text()
        start = source.index('    s_w = muse_board->width;')
        layout = source[start:source.index('    lv_display_t *disp =', start)]
        # Compile the actual upstream size selection, rather than maintaining a
        # second implementation of the layout formula in the test.
        prefix = """
#include <assert.h>
#include <stdbool.h>
#define MUSE_PX_W 64
struct board { int width, height, avatar_px; bool round; };
static void check(struct board *muse_board, int expected, bool compact) {
    int s_w, s_h, s_canvas_px, s_dy;
    bool s_small, s_tall;
"""
        calls = ''.join(f'check(&(struct board){{{b.width},{b.height},{b.avatar_override},{int(b.round)}}}, {b.avatar}, {int(b.compact)});\n' for b in BOARDS.values())
        code = prefix + layout + '(void)s_tall; assert(s_canvas_px==expected); assert(s_small==compact); }\nint main(void) {\n' + calls + '}\n'
        with tempfile.TemporaryDirectory() as tmp:
            c = Path(tmp)/'layout.c'; c.write_text(code)
            exe = Path(tmp)/'layout'
            subprocess.run([os.environ.get('CC', 'cc'), '-Wall', '-Werror', str(c), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True)

    def test_build_uses_each_boards_target_and_overlay(self):
        for alias, board in BOARDS.items():
            cmd = command(alias, 'build')
            self.assertIn(f'-DIDF_TARGET={board.target}', cmd)
            self.assertIn(f'-DSDKCONFIG=build-muse-{board.profile}/sdkconfig', cmd)
            self.assertTrue(any('devices/sdkconfig.muse-'+board.profile+';' in s for s in cmd))
            self.assertEqual(cmd[-1], 'build')

    def test_flash_preserves_sdk_special_uploaders(self):
        for alias in BOARDS:
            self.assertEqual(command(alias, 'flash', '/dev/test'),
                             ['bash', 'tools/muse/board.sh', 'flash', alias, '/dev/test'])
            with self.assertRaises(ValueError):
                command(alias, 'flash')

    def test_configure_opens_menuconfig(self):
        self.assertEqual(command('sticks3', 'configure')[-1], 'menuconfig')
