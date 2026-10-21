from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from install import install, REVISION, RUNTIME

SDK = Path(os.environ.get('MUSE_TEST_SDK', ROOT.parent/'muse-gadget-sdk'))


@unittest.skipUnless((SDK/'.git').exists(), 'Set MUSE_TEST_SDK to a pinned SDK checkout')
class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='celery-install-test-')
        self.addCleanup(self.tmp.cleanup)
        self.sdk = Path(self.tmp.name)/'sdk'
        subprocess.run(['git', 'clone', '--quiet', '--shared', '--no-checkout', str(SDK), str(self.sdk)], check=True)
        subprocess.run(['git', '-C', str(self.sdk), 'fetch', '--quiet', 'origin', REVISION], check=True)
        subprocess.run(['git', '-C', str(self.sdk), 'checkout', '--quiet', REVISION], check=True)

    def diff(self):
        return subprocess.check_output(['git', '-C', str(self.sdk), 'diff'])

    def test_clean_install_and_repeat(self):
        install(self.sdk, check=True)
        self.assertEqual(self.diff(), b'')
        install(self.sdk)
        first = self.diff()
        install(self.sdk)
        self.assertEqual(first, self.diff())
        subprocess.run(['git', '-C', str(self.sdk), 'diff', '--check'], check=True)

    def test_wrong_revision_is_rejected_without_changes(self):
        subprocess.run(['git', '-C', str(self.sdk), '-c', 'user.name=Test',
                        '-c', 'user.email=test@example.invalid', 'commit',
                        '--allow-empty', '-qm', 'Unsupported revision'], check=True)
        with self.assertRaisesRegex(RuntimeError, 'supported SDK revision'):
            install(self.sdk)
        self.assertEqual(self.diff(), b'')
        self.assertFalse((self.sdk/'esp32/components/muse/avatar').exists())

    def test_upgrade_menu_only_install_adds_timing(self):
        subprocess.run(['git', '-C', str(self.sdk), 'apply',
                        str(ROOT/'patches/muse-character-menu.patch')], check=True)
        install(self.sdk)
        subprocess.run(['git', '-C', str(self.sdk), 'apply', '--reverse', '--check',
                        str(ROOT/'patches/muse-character-timing.patch')], check=True)

    def test_conflicting_timing_is_preserved_without_partial_install(self):
        source = self.sdk/'esp32/components/muse/muse_input.c'
        source.write_text(source.read_text().replace(
            'vTaskDelay(pdMS_TO_TICKS(GOODBYE_MS));', 'my_custom_shutdown_wait();'))
        before = self.diff()
        with self.assertRaisesRegex(RuntimeError, 'conflict'):
            install(self.sdk)
        self.assertEqual(self.diff(), before)
        self.assertFalse((self.sdk/'esp32/components/muse/avatar').exists())

    def test_conflicting_menu_is_preserved(self):
        menu = self.sdk/'esp32/components/muse/muse_menu.c'
        menu.write_text('/* Local replacement menu */\n')
        before = self.diff()
        with self.assertRaisesRegex(RuntimeError, 'conflict'):
            install(self.sdk)
        self.assertEqual(self.diff(), before)

    def test_user_avatar_is_preserved(self):
        avatar = self.sdk/'esp32/components/muse/avatar'
        avatar.mkdir()
        source = avatar/'muse_pixel.c'
        source.write_text('/* Local artwork */\n')
        with self.assertRaisesRegex(RuntimeError, 'differs'):
            install(self.sdk)
        self.assertEqual(source.read_text(), '/* Local artwork */\n')
        self.assertEqual(self.diff(), b'')

    def test_upgrade_previous_artwork(self):
        install(self.sdk)
        avatar = self.sdk/'esp32/components/muse/avatar'
        for revision in ('362e373', '5825a73', '33612ec', '76b5e7f', '17a575f', '26c3610', '3359df2'):
            with self.subTest(revision=revision):
                old_files = subprocess.check_output(['git', '-C', str(ROOT), 'ls-tree',
                    '-r', '--name-only', revision, 'avatar/'], text=True).splitlines()
                for name in RUNTIME:
                    if 'avatar/' + name not in old_files:
                        (avatar/name).unlink(missing_ok=True)
                        continue
                    previous = subprocess.check_output(['git', '-C', str(ROOT), 'show',
                        revision + ':avatar/' + name])
                    (avatar/name).write_bytes(previous)
                install(self.sdk, check=True)
                install(self.sdk)
                for name in RUNTIME:
                    self.assertEqual((avatar/name).read_bytes(), (ROOT/'avatar'/name).read_bytes())

    def test_upgrade_three_character_roster(self):
        install(self.sdk)
        avatar = self.sdk/'esp32/components/muse/avatar'
        for name in ('muse_pixel.c', 'characters.h'):
            (avatar/name).write_bytes(subprocess.check_output(['git', '-C', str(ROOT), 'show',
                'e361b7bdd9eb086b060ec1dbe12b586e99adb4df:avatar/' + name]))
        (avatar/'eggman/sprites.h').unlink()
        install(self.sdk)
        for name in RUNTIME:
            self.assertEqual((avatar/name).read_bytes(), (ROOT/'avatar'/name).read_bytes())

    def test_modified_previous_artwork_is_preserved(self):
        install(self.sdk)
        source = self.sdk/'esp32/components/muse/avatar/muse_pixel.c'
        source.write_bytes(subprocess.check_output(['git', '-C', str(ROOT), 'show',
            '76b5e7f:avatar/muse_pixel.c']) + b'\n/* Local modification */\n')
        before = source.read_bytes()
        with self.assertRaisesRegex(RuntimeError, 'differs'):
            install(self.sdk)
        self.assertEqual(source.read_bytes(), before)

    def test_upgrade_keeps_unrelated_changes(self):
        install(self.sdk)
        avatar = self.sdk/'esp32/components/muse/avatar'
        for name in RUNTIME:
            target = avatar/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/'avatar'/name, target)
        unrelated = self.sdk/'README.md'
        unrelated.write_text('My local README\n')
        install(self.sdk)
        self.assertEqual(unrelated.read_text(), 'My local README\n')
