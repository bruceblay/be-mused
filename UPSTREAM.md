# Staying in sync with Muse

This is a character pack, not a fork of Muse Gadget SDK. Muse owns the device drivers, conversations, pairing, audio, and base interface. This repository supplies the animations and adds a character picker to the button and touch menus.

## Current version

The pack is pinned to [`812c46f9fe42b69d916613a9dc702cbac5ff7b54`](https://github.com/facebookincubator/muse-gadget-sdk/commit/812c46f9fe42b69d916613a9dc702cbac5ff7b54). The installer checks the exact revision before changing files. Following upstream `main` without updating the integration is not supported.

This upgrade brings upstream's text-reply fix, more reliable conversation timeouts, reply filtering, memory fixes, Watcher power management, and additional full-UI boards. Text replies appear as paced captions; upstream does not currently fetch spoken replies from the Muse TTS service.

The optional CJK font is disabled by `firmware/character-pack.defaults` to reserve flash for the animation pack. This also overrides the AI Passport's upstream default on a fresh configuration. Existing configuration choices take precedence over defaults; if you enable that font, check the resulting firmware size.

## Updating the pin

Updates are deliberate, tested changes. There is no automatic merge or device update.

1. Fetch upstream and review changes since the current pin, especially avatar APIs, layouts, menu input, and memory use.
2. Test in a separate SDK checkout. Adapt `patches/muse-character-menu.patch` and `patches/muse-character-timing.patch`, update `tools/install.py`, the CI revision, documentation links, and the unmodified headers in `sdk-headers/`.
3. Run the installer, repeat-install and preservation tests, menu navigation tests, and renderer sanitizers. Run the upstream host suite against the installed pack.
4. Build every advertised board with ESP-IDF v6.0.1. Record the signed application's remaining space and any failures in [TESTING.md](TESTING.md). A new upstream driver alone does not establish pack support.
5. Check new avatar sizes and controls, regenerate the [device mockups](DEVELOPMENT.md#readme-device-previews), and record physical testing separately from successful builds.
6. Commit the new pin and integration together. GitHub CI verifies installation and host checks against that pinned revision on each push and pull request.

For an existing installation, follow the [SDK migration instructions](INSTALL.md#update). Keep custom SDK changes and credentials in the old checkout until reconciled; the installer never switches SDK revisions or overwrites unknown avatar edits.
