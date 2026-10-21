# Testing and known issues

Checked on 2026-10-10 with ESP-IDF v6.0.1 and Muse SDK revision `812c46f9fe42b69d916613a9dc702cbac5ff7b54`. Eggman checks below were added on 2026-10-21 against the same toolchain and SDK.

## Eggman front-reveal mappings — 2026-10-21

- Startup uses the 24-frame close-up reveal once, then holds neutral. Error uses the 26-frame pants-lowering shot once, then holds the revealed pose with the error indicator. Power off plays that same complete lowering shot before a 0.35-second fade.
- The timing integration gives Eggman 1.8 seconds at startup and 2.2 seconds at shutdown. Other characters keep the SDK’s 1.4-second startup and 1.5-second shutdown durations.
- All five avatars pass the renderer sanitizers. New checks cover source-frame order, final-pose holds, repeated state entry, error/off priority over Happy, complete shutdown playback, and black output by shutdown time.
- All 15 pack tests pass, including upgrades from an existing menu-only integration and refusal to partially install over conflicting shutdown code. SDK suite: 222 tests, 221 passed, 1 skipped for missing host PSA Crypto dependencies.
- StickS3 build passes: app `0x371000` bytes, 444 KiB free (11%). Flashed with written-data hash verification and preserved NVS; the first status check reported Wi-Fi and Muse connected. A subsequent boot log reached Muse startup and ready, restored Eggman, and contained no panic. Console-driven startup, error, and off animations completed without panic/reset markers; the device was returned to idle and again reported Wi-Fi and Muse connected. The physical power-cut timing was not exercised. Other board builds predate this mapping update.

## Eggman ready pose and project rename — 2026-10-21

- Renamed the GitHub repository and local checkout to `be-mused`, updated the Git remote, project heading, notice, and clone instructions. The old local path is a compatibility symlink for existing chats and build references.
- Replaced Eggman’s idle gesture loop with the user-selected open-mouth waiting pose, extracted from 0:09.00 in the source footage. The pack now has 73 samples; boot and the other states keep their original footage.
- Renderer checks pass for all five avatars, seven modes, and seventeen output sizes, including exact held-ready pixels and return from happy. All 13 pack tests pass. The installer accepts the previous Eggman runtime through its recorded hashes.

- Clean StickS3 build passes from the renamed checkout: app `0x371000` bytes, 444 KiB free (11%). The ready-pose revision was flashed with written-data hash verification; NVS was preserved. Boot logs confirm Eggman is loaded, but two USB-reset startup checks stalled during Wi-Fi startup; the user confirmed the device worked after a physical restart.

## Eggman addition — 2026-10-21

- Seventy-two real video samples extracted, with original frame order and 15 fps cadence. Reviewed the source crops, cutouts, and renderer previews for gesture, neutral, chewing, turn, and rear-facing animations. Source motion and transition ghosting remain.
- Five avatars pass AddressSanitizer/UBSan checks across seven modes and seventeen output sizes. Eggman and Oyster match uncompressed RGB565 samples across complete loops and state changes, including zero audio levels and Oyster's boot/off shifts.
- Lossless storage of Eggman and Oyster matches the previous uncompressed renderer byte-for-byte across 4,480 poses. Existing character art and timing are unchanged.
- Thirteen pack unit tests pass, including upgrade from the three-character roster, Eggman selection, Back, and stable Default pet index 3.
- SDK host suite: 222 tests, 221 passed and 1 skipped for missing host PSA Crypto dependencies.
- StickS3 build passes: app `0x371000` bytes, with 444 KiB free (11%). Waveshare C6 1.8 build passes: app `0x3b1000` bytes, with 316 KiB free (8%). Both include the full roster; flash partitions are unchanged.
- Flashed the Eggman build to the identified StickS3 with written-data hash verification; NVS was preserved. Initial startup panicked during Wi-Fi startup and left the console unresponsive; the pre-flash firmware also panicked during Wi-Fi startup. After a physical restart and another USB reset, the board completed startup, joined Wi-Fi, and answered status requests without a panic in the recovery log.
- Selected Eggman through the device menu (confirmed by its `selected Eggman` log), exercised idle, listening, thinking, speaking, and happy through the console, and left it in idle. The subsequent status request succeeded, with no panic or reset markers during the animation check. Physical visual review and long-term stability remain unverified. Other board builds below predate Eggman.

## Firmware builds — before Eggman

The SDK upgrade uses clean, separate checkouts with only the character-pack integration applied. Upstream now includes the text-reply workaround previously maintained in the local development SDK. All profiles carry the same approved animation frames.

| Profile | Result | App partition free | Physical device |
| --- | --- | --- | --- |
| StickS3 | Passed | 5% | Tested |
| StickC Plus2 | Passed | 6% | Not tested |
| AIPI Lite | Passed | 8% | Not tested |
| SenseCAP Watcher | Passed | 6% | Not tested |
| Waveshare S3 1.75C | Passed | 8% | Not tested |
| Waveshare C6 1.8 | Passed | 1% | Not tested |

These earlier uncompressed builds left about 60 KiB on Waveshare C6. The lossless storage added with Eggman increases its free space to 316 KiB without changing its partition layout.

A successful build does not verify touch input, audio, power use, or frame rate on that board. Touchscreen character selection still needs physical-device testing.

## Automated checks

- Five avatars, seven Muse modes, and seventeen output sizes under AddressSanitizer and UBSan.
- Complete custom-character animation cycles, including Tayne's 1.6-second video loops. Every idle, listening, and thinking frame must match its packed source frame, in order, at exact 15 fps boundaries.
- Tayne's speech sequence follows its source frames even with zero or low audio-level input, restarts on re-entry to speaking mode, and returns to idle when that mode ends. Microphone levels do not interrupt the listening dance; thinking dots remain below the boots.
- Tayne matches the prior renderer across 1,680 sampled poses.
- Oyster's idle, listening, speaking, and thinking loops follow the packed source frames, including the printout's held smile, and happy returns to idle.
- Celery Man’s three video loops follow the approved source frames across idle, listening, thinking, speaking, and happy. Checks cover repeated loops, zero audio level, state re-entry, and return from happy to idle.
- Partial display strips match full-frame output; buffer guards remain intact.
- Default pet output matches the original SDK renderer, including after switching from each dancer.
- Clean and repeated installation; refusal to overwrite conflicting menus or custom artwork; rejection of an unsupported SDK revision before writing; preservation of unrelated edits. Older SDK checkouts use the migration steps in [INSTALL.md](INSTALL.md#update).
- Upgrade from the previous dance artwork, with changed local artwork still protected.
- Board profiles use their own chip target, configuration, and SDK flash helper. Native avatar sizes are checked by compiling upstream’s actual layout calculation.
- Character-menu keyboard navigation, wraparound, Back/cancel, default-pet selection, save failures, and protection against accidental selection with Left/Right.
- Fifteen pack unit tests passed.
- All 19 README mockups exported from the native renderer: 176 frames and 11.73 seconds each, cycling through all four custom characters. Each includes Oyster’s printout and Eggman’s startup reveal, ready pose, and pants-lowering shutdown. Frame counts, GIF durations, segment metadata, file sizes, and README image links were checked; Eggman contact sheets for all boards and the StickS3 transition sequence were visually reviewed.
- SDK host suite: 222 tests, 221 passed, 1 skipped because the host lacks PSA Crypto development headers/libraries. The suite ran against an SDK checkout with this pack installed.

The speaking-freeze regression fails against the previous renderer: zero audio-level input holds one frame there. The corrected renderer advances through all twelve speech frames at zero, low, and normal levels. Its StickS3 firmware build passed and was flashed with hash verification.

GitHub Actions runs the renderer, profile, and installer tests on each push. Full firmware builds are currently checked locally.

## StickS3 hardware checks

The historical hardware results below are from the previous SDK revision. The upgraded SDK was flashed and checked with Eggman on 2026-10-21; startup recovery and animation checks are recorded above. New boards are build-tested only.

On the previous SDK, flashing passed written-data hash verification and preserved pairing. The board connected to Muse, selected each dancer, restored Default pet, and retained its saved character across a restart. Console-driven idle, listening, thinking, speaking, and happy states remained responsive.

Tayne's speech-freeze correction and the Celery Man and Oyster video updates were flashed successfully. Oyster's animations were reviewed visually on the device on 2026-10-08. Short boot checks reached Muse startup without a panic or reboot loop, though intermittent power failures remain unresolved.

## Known issues

Intermittent brownouts can occur during Wi-Fi startup or a USB-driven reset. The console may stop responding afterward. A physical restart restored the test unit; on another occasion it recovered by itself. The cause remains unresolved, and power protections remain enabled.

Long-term stability, real spoken-audio testing, and physical frame timing remain unverified. Please remove credentials and personal device details before sharing logs in an issue.
