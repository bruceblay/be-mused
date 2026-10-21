"""Exercise the installed menu's real key handler with host-side UI fakes."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
SDK = Path(os.environ.get('MUSE_TEST_SDK', ROOT.parent/'muse-gadget-sdk')).resolve()


def function(source, signature):
    start = source.index(signature)
    body = source.index('{', start)
    depth = 1
    end = body + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


@unittest.skipUnless((SDK/'.git').exists(), 'Set MUSE_TEST_SDK to a pinned SDK checkout')
class MenuTests(unittest.TestCase):
    def test_character_keys_and_default_pet(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            for name in ('CMakeLists.txt', 'muse_menu.c', 'muse_settings_ui.c'):
                rel = 'esp32/components/muse/' + name
                dest = work/rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                from install import REVISION
                dest.write_bytes(subprocess.check_output(['git', '-C', str(SDK), 'show', REVISION+':'+rel]))
            subprocess.run(['git', 'apply', str(ROOT/'patches/muse-character-menu.patch')], cwd=work, check=True)
            source = (work/'esp32/components/muse/muse_menu.c').read_text()
            header = (SDK/'esp32/components/muse/muse_menu.h').read_text()
            enums = '\n'.join(re.findall(r'typedef enum \{.*?\} \w+;', source, re.S))
            enums += '\n' + re.search(r'typedef enum \{.*?\} muse_menu_key_t;', header, re.S)[0]
            # Only Character/Pet cases need their real activation behavior here;
            # unrelated settings are counted by the fake to catch accidental activation.
            activate = function(source, 'static void activate(')
            cases = activate[activate.index('#ifdef MUSE_CUSTOM_CHARACTERS'):activate.index('    case ITEM_VOLUME:')]
            c = r'''
#include <assert.h>
#include <stdbool.h>
#define MUSE_CUSTOM_CHARACTERS 1
''' + enums + r'''
static int s_character_sel, s_sel, chosen=-1, saves, activations, pokes, happies;
static view_t s_view;
static void *s_title;
static bool save_ok=true;
static int muse_character_count(void) { return 5; }
static int muse_character_current(void) { return 2; }
#define MUSE_CHARACTER_DEFAULT 3
static bool muse_character_select(int n) { saves++; if (save_ok) chosen=n; return save_ok; }
static void refresh(void) {}
static void set_text(void *p, const char *s) { (void)p; (void)s; }
static void show(view_t v) { s_view=v; }
static void muse_menu_close(void) { s_view=VIEW_CLOSED; }
static void muse_state_poke(void) { pokes++; }
static void muse_state_make_happy(void) { happies++; }
static void open_menu(void) { show(VIEW_LIST); }
static void muse_input_request_power_off(void) { assert(0); }
static void muse_state_set_caption(const char *s) { (void)s; assert(0); }
static void muse_link_reset_setup(void) { assert(0); }
static void activate(int item, int direction) {
    (void)direction;
    switch(item) {
''' + cases + r'''
    default: activations++; break;
    }
}
''' + function(source, 'static void handle(') + r'''
int main(void) {
    s_view=VIEW_LIST; s_sel=ITEM_CHARACTER;
    handle(MUSE_MENU_RIGHT); handle(MUSE_MENU_LEFT);
    assert(s_view==VIEW_LIST && saves==0 && activations==0);
    handle(MUSE_MENU_SELECT);
    assert(s_view==VIEW_CHARACTER && s_character_sel==2);
    handle(MUSE_MENU_UP); assert(s_character_sel==1 && saves==0);
    handle(MUSE_MENU_DOWN); assert(s_character_sel==2 && saves==0);
    handle(MUSE_MENU_RIGHT); assert(saves==0 && s_view==VIEW_CHARACTER);
    handle(MUSE_MENU_BACK); assert(saves==0 && s_view==VIEW_LIST);
    handle(MUSE_MENU_SELECT); handle(MUSE_MENU_LEFT);
    assert(saves==0 && s_view==VIEW_LIST);
    handle(MUSE_MENU_SELECT); s_character_sel=0;
    handle(MUSE_MENU_UP); assert(s_character_sel==5);
    handle(MUSE_MENU_DOWN); assert(s_character_sel==0);
    handle(MUSE_MENU_SELECT);
    assert(chosen==0 && saves==1 && s_view==VIEW_CLOSED && pokes==1 && happies==1);
    s_view=VIEW_CHARACTER; s_character_sel=5;
    handle(MUSE_MENU_SELECT); assert(s_view==VIEW_LIST && saves==1);
    s_view=VIEW_CHARACTER; s_character_sel=2; save_ok=false;
    handle(MUSE_MENU_SELECT); assert(s_view==VIEW_CHARACTER && chosen==0 && saves==2);
    s_view=VIEW_LIST; s_sel=ITEM_PET; save_ok=true;
    handle(MUSE_MENU_LEFT); handle(MUSE_MENU_RIGHT); assert(saves==2);
    handle(MUSE_MENU_SELECT); assert(chosen==3 && saves==3 && s_view==VIEW_CLOSED);
    s_view=VIEW_CHARACTER; s_character_sel=4;
    handle(MUSE_MENU_SELECT); assert(chosen==4 && saves==4 && s_view==VIEW_CLOSED);
    s_view=VIEW_LIST; s_sel=ITEM_VOLUME;
    handle(MUSE_MENU_RIGHT); assert(activations==1);
    return 0;
}
'''
            (work/'menu.c').write_text(c)
            compiler = os.environ.get('CC', 'cc')
            self.assertIsNotNone(shutil.which(compiler))
            subprocess.run([compiler, '-Wall', '-Werror', '-fsanitize=address,undefined', str(work/'menu.c'), '-o', str(work/'menu')], check=True)
            subprocess.run([str(work/'menu')], check=True)
