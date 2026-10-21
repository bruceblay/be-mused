# Devices and screen sizes

The pack uses the display drivers and layout already provided by the pinned [Muse SDK](https://github.com/facebookincubator/muse-gadget-sdk/blob/812c46f9fe42b69d916613a9dc702cbac5ff7b54/esp32/devices/README.md).

| Device | Build name | Display | Avatar area | Controls |
| --- | --- | --- | --- | --- |
| M5Stack StickS3 | `sticks3` | 135×240 | 128×128 | Buttons |
| M5Stack StickC Plus2 | `plus2` | 135×240 | 128×128 | Buttons |
| AIPI Lite | `aipi` | 128×128 | 96×96 | Buttons |
| SenseCAP Watcher | `watcher` | 412×412, round | 256×256 | Touchscreen |
| Waveshare S3 1.75C | `s3` | 466×466, round | 320×320 | Touchscreen |
| Waveshare C6 1.8 | `c6` | 368×448 | 320×320 | Touchscreen |
| Waveshare S3 1.75 | `s3n` | 466×466, round | 320×320 | Touchscreen |
| Waveshare S3 2.16 | `s3-216` | 480×480 | 320×320 | Touchscreen |
| Espressif ESP32-S3-BOX-3 | `box3` | 320×240 | 160×160 | Touchscreen |
| Waveshare C6 2.06 | `c6-206` | 410×502 | 320×320 | Touchscreen |
| M5Stack Cardputer ADV | `cardputer-adv` | 240×135 | 90×90 | Keyboard |
| M5Stack StopWatch | `stopwatch` | 466×466, round | 320×320 | Touchscreen |
| M5Stack CoreS3 | `cores3` | 320×240 | 160×160 | Touchscreen |
| M5Stack Core2 v1.0 | `core2` | 320×240 | 160×160 | Touchscreen |
| Freenove FNK0104B | `fnk0104b` | 240×320 | 240×240 | Touchscreen |
| Guition JC3248W535 | `jc3248w535` | 320×480 | 320×320 | Touchscreen |
| Waveshare S3 LCD 7 | `lcd7` | 800×480 | 288×288 | Touchscreen |
| VN ESP32-S3 1.83 | `vn183` | 284×240 | 160×160 | Buttons |
| FoloToy AI Passport | `ai-passport` | 240×320 | 240×240 | Buttons |

Firmware build results are recorded in [TESTING.md](TESTING.md). StickS3 has been checked on a physical device with the current SDK and Eggman animations. The other profiles still need physical verification. Cardputer ADV and AI Passport remain experimental upstream.

## Controls

Button boards use their existing menu and select buttons. Cardputer ADV uses Esc to open the menu, arrows to navigate, and Enter to choose. Esc or Left leaves the character picker without saving. On touchscreen boards, swipe to Settings and open **Character**, then tap a name. **Pet** restores the default avatar on both interfaces. Touching a character on the main screen retains Muse's normal happy reaction.

## Scaling

The table lists the normal avatar area, not the full panel. Muse leaves space for captions and controls, and keeps art away from the edges of round displays. Some UI states resize the avatar further.

The same 64×64 sprites scale to each square area with nearest-neighbor sampling. The renderer supports sizes from 1 to 512 pixels, including sizes between whole multiples of 64. Scaling keeps the character's proportions; it does not generate new detail. No separate sprite pack is needed per board.

Tests cover native avatar sizes, panel widths, and intermediate sizes. Use the [preview exporter](DEVELOPMENT.md#artwork-and-previews) to inspect a particular size.

## Hardware differences

The C6 boards, Cardputer ADV, and AI Passport have no PSRAM: upstream Muse uses voice notes with text replies and does not support image display on these profiles. All current profiles receive caption replies rather than Muse TTS audio. The StickC Plus2 has a buzzer rather than the StickS3's speaker. The character pack inherits these limits.

Core2 support follows upstream's **v1.0** hardware profile. Freenove FNK0104B needs an added I2S microphone for push-to-talk. The seven-inch Waveshare LCD has no onboard microphone or speaker; it can show the avatar and Muse status, but is not a voice companion by itself. Check upstream's device notes before choosing hardware.

Devices with only a status screen, an LED ring, or e-paper do not use this avatar interface. Supporting them requires a separate UI or SDK port. New boards should first work with Muse's original pet before adding this pack.
