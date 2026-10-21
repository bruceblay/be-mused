"""Muse full-UI profiles from the pinned SDK's devices/ overlays and muse_ui.c."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Board:
    name: str
    profile: str
    target: str
    width: int
    height: int
    avatar: int
    touch: bool
    round: bool = False
    keyboard: bool = False
    avatar_override: int = 0

    @property
    def compact(self):
        return self.height < 200 or self.width < 300 or (self.width > self.height and self.height < 320)

    @property
    def controls(self):
        return 'Keyboard' if self.keyboard else 'Touchscreen' if self.touch else 'Buttons'


BOARDS = {
    'sticks3': Board('M5Stack StickS3', 'm5stack-sticks3', 'esp32s3', 135, 240, 128, False),
    'plus2': Board('M5Stack StickC Plus2', 'm5stack-stickc-plus2', 'esp32', 135, 240, 128, False),
    'aipi': Board('AIPI Lite', 'aipi', 'esp32s3', 128, 128, 96, False),
    'watcher': Board('SenseCAP Watcher', 'sensecap-watcher', 'esp32s3', 412, 412, 256, True, True),
    's3': Board('Waveshare S3 1.75C', 'waveshare-s3-175c', 'esp32s3', 466, 466, 320, True, True),
    'c6': Board('Waveshare C6 1.8', 'waveshare-c6-18', 'esp32c6', 368, 448, 320, True),
    's3n': Board('Waveshare S3 1.75', 'waveshare-s3-175', 'esp32s3', 466, 466, 320, True, True),
    's3-216': Board('Waveshare S3 2.16', 'waveshare-s3-216', 'esp32s3', 480, 480, 320, True),
    'box3': Board('Espressif ESP32-S3-BOX-3', 'espressif-box-3', 'esp32s3', 320, 240, 160, True),
    'c6-206': Board('Waveshare C6 2.06', 'waveshare-c6-206', 'esp32c6', 410, 502, 320, True),
    'cardputer-adv': Board('M5Stack Cardputer ADV', 'm5stack-cardputer-adv', 'esp32s3', 240, 135, 90, False, keyboard=True),
    'stopwatch': Board('M5Stack StopWatch', 'm5stack-stopwatch', 'esp32s3', 466, 466, 320, True, True),
    'cores3': Board('M5Stack CoreS3', 'm5stack-cores3', 'esp32s3', 320, 240, 160, True),
    'core2': Board('M5Stack Core2 v1.0', 'm5stack-core2', 'esp32', 320, 240, 160, True),
    'fnk0104b': Board('Freenove FNK0104B', 'fnk0104b', 'esp32s3', 240, 320, 240, True),
    'jc3248w535': Board('Guition JC3248W535', 'guition-jc3248w535', 'esp32s3', 320, 480, 320, True),
    'lcd7': Board('Waveshare S3 LCD 7', 'waveshare-s3-lcd7', 'esp32s3', 800, 480, 288, True, avatar_override=288),
    'vn183': Board('VN ESP32-S3 1.83', 'vn-s3-183', 'esp32s3', 284, 240, 160, False),
    'ai-passport': Board('FoloToy AI Passport', 'ai-passport', 'esp32c3', 240, 320, 240, False),
}
