# Artwork

## Tayne

All of Tayne's poses use actual frames from the [supplied sketch](https://www.youtube.com/watch?v=a8K6QUPmv8Q).

| Animation | Video segment | Samples | Sprite sheet |
| --- | --- | --- | --- |
| Idle: low, wide-legged bounce | 1:06.65–1:08.25 | 24 | [video-idle.png](avatar/tayne/video-idle.png) |
| Happy: Flarhgunnstow | 1:14.40–1:16.00 | 24 | [video-happy.png](avatar/tayne/video-happy.png) |
| Listening: sideways arm swing | 1:02.03–1:02.83 | 12 | [video-listening.png](avatar/tayne/video-listening.png) |
| Thinking: raised-arm kicks | 1:12.80–1:13.47 | 10 | [video-thinking.png](avatar/tayne/video-thinking.png) |
| Speaking: frontal greeting | 0:56.50–0:57.30 | 12 | [video-front.png](avatar/tayne/video-front.png) |

Each sequence uses consecutive samples at 15 fps. Backgrounds are removed before scaling onto a black 64×64 canvas. Recorded masks remove the old window edges around the extended hands and boots. The portrait mask preserves enclosed highlights such as reflections in the sunglasses. The approved idle and happy sheets are unchanged.

Frame order and cadence follow the footage, with no generated dance poses, added mirroring, or invented transitions. These short excerpts repeat as loops; their ends are not blended. Clipping already present in the source remains. Speaking loops while Muse is in speaking mode, independently of the audio meter. It does not track individual phonemes. Boot reuses the Flarhgunnstow dance. Error and off use a filmed neutral frame.

[video-clips.json](avatar/tayne/video-clips.json) records timestamps, crops, keys, and masks. With FFmpeg, Pillow, and a local 1920×1080 copy of the video, rebuild the sheets with:

```sh
python3 avatar/tayne/extract_video.py /path/to/video.mp4
python3 avatar/tayne/pack_sprites.py
```

For an input trimmed to start at a known source timestamp, pass `--source-start SECONDS`. Use `--clip listening` to rebuild one sequence. The video and its audio are not included in this repository.

## Celery Man

Celery Man uses three consecutive video excerpts from the same sketch:

| Animation | Video segment | Samples | Sprite sheet |
| --- | --- | --- | --- |
| Hip sway: idle and thinking | 0:23.40–0:25.00 | 24 | [video-hip-sway.png](avatar/celery-man/video-hip-sway.png) |
| Raised-fist shuffle: listening and speaking | 0:28.03–0:29.63 | 24 | [video-raised-fists.png](avatar/celery-man/video-raised-fists.png) |
| 4d3d3: happy | 0:37.43–0:39.03 | 24 | [video-4d3d3.png](avatar/celery-man/video-4d3d3.png) |

The loops run at 15 fps, preserving source order and timing. A narrow background key retains the hand highlights. Recorded masks protect white fabric, including the two 4d3d3 frames where the shirt meets the pale background. Masks restore source pixels; they do not redraw the dancer. GIF previews use a shared palette without dithering.

[source-clips.json](avatar/celery-man/source-clips.json) records the extraction settings. With FFmpeg, Pillow, and a local 1920×1080 copy of the video:

```sh
python3 avatar/celery-man/extract_video.py /path/to/video.mp4
python3 avatar/celery-man/pack_sprites.py
python3 avatar/tayne/export_preview.py --character celery-man
```

For a trimmed source, pass `--source-start SECONDS` to the extractor. The three sheets pack into seventy-two RGB565 frames. The earlier generated [source sheet](avatar/celery-man/source.png) and [prompt](avatar/celery-man/imagegen-prompt.txt) remain as history; the firmware uses the video sheets.

## Oyster

Oyster uses four consecutive video excerpts from the same sketch:

| Animation | Video segment | Samples | Sprite sheet |
| --- | --- | --- | --- |
| Headbang: idle | 0:40.00–0:40.53 | 8 | [video-headbang.png](avatar/oyster/video-headbang.png) |
| Arms back: listening | 0:41.00–0:41.67 | 10 | [video-arms-back.png](avatar/oyster/video-arms-back.png) |
| Greeting: speaking and happy | 0:39.03–0:39.57 | 8 | [video-greeting.png](avatar/oyster/video-greeting.png) |
| Printout: thinking | 0:44.55–0:46.42 | 28 | [video-printout.png](avatar/oyster/video-printout.png) |

The loops run at 15 fps in source order. Thinking plays the whole printout, holds the finished smile for 0.6 seconds, then prints again. The printout extractor tracks the upper paper edge to remove the rear tray and room, keeping the paper, portrait, and printer lip. GIF previews use a shared palette without dithering.

[source-clips.json](avatar/oyster/source-clips.json) and [printout-source.json](avatar/oyster/printout-source.json) record the extraction settings. With FFmpeg, Pillow, NumPy, and a local 1920×1080 copy of the video:

```sh
python3 avatar/oyster/extract_video.py /path/to/video.mp4
python3 avatar/oyster/extract_print.py /path/to/video.mp4
python3 avatar/oyster/pack_sprites.py
python3 avatar/tayne/export_preview.py --character oyster
```

The four sheets pack into fifty-four RGB565 frames. Lossless storage reduces them to 129,148 bytes to make room for Eggman on smaller devices; Oyster’s decoded pixels, frame order, and timing are unchanged. The earlier generated [source sheet](avatar/oyster/source.png) and [prompt](avatar/oyster/imagegen-prompt.txt) remain as history; the firmware uses the video sheets.

## Eggman

Eggman uses filmed game animation from [“Eggman Game” — I Think You Should Leave with Tim Robinson, Netflix Is a Joke](https://www.youtube.com/watch?v=K0OSfbPJFa4).

| Animation | Video segment | Samples | Sprite sheet |
| --- | --- | --- | --- |
| Waiting: ready/idle | 0:09.00 (held) | 1 | [video-waiting.png](avatar/eggman/video-waiting.png) |
| Front reveal: startup | 1:50.40–1:52.00 | 24 | [video-front-reveal.png](avatar/eggman/video-front-reveal.png) |
| Pants lowering: error, power off | 1:43.85–1:45.58 | 26 | [video-front-lower.png](avatar/eggman/video-front-lower.png) |
| Neutral: listening | 1:52.20 | 1 held frame | [video-neutral.png](avatar/eggman/video-neutral.png) |
| Chewing: speaking | 0:08.60–0:09.60 | 15 | [video-chew.png](avatar/eggman/video-chew.png) |
| Turning: thinking | 1:52.90–1:53.90 | 15 | [video-turn.png](avatar/eggman/video-turn.png) |
| Rear-facing crouch: happy | 1:56.65–1:58.38 | 26 | [video-rear.png](avatar/eggman/video-rear.png) |

Each moving sequence uses consecutive samples at 15 fps. End timestamps are exclusive. The chewing and waiting crops come from the same shot, after the cursor leaves the character. Close-up footage supplies the other poses. The original blue screen tint, camera movement, and filmed transition ghosting remain. Conversation and happy excerpts repeat directly. Startup, error, and power off play once and hold their last source frame; power off then fades out. No clips blend their ends, mirror frames, interpolate movement, or draw replacement poses. Ready holds the actual open-mouth waiting frame; listening holds the closed-mouth neutral frame, and speaking plays independently of audio level. Thinking dots, happy sparkles, error dimming, and the power-off fade are Muse status effects; Eggman has no added bobbing or translation.

The extractor fits the smooth monitor background from each crop’s border, detects the original dark outline, and fills enclosed character regions. Background openings between arms and legs remain transparent. This edits the matte only; the face, limbs, and body retain source RGB pixels. It composites onto black before downsampling to 64×64, then packs 108 RGB565 frames. Padding cells in the sheets are excluded. Lossless pixel runs and changes from earlier frames reduce their storage from 864 KiB to 66,429 bytes, including lookup tables; decoded pixels are identical to the uncompressed RGB565 sheets.

[source-clips.json](avatar/eggman/source-clips.json) records the source, timestamps, crops, sizes, and frame counts. With FFmpeg, Pillow, NumPy, and a local 1920×1080 copy:

```sh
python3 avatar/eggman/extract_video.py /path/to/eggman.mp4 --qa /tmp/eggman-cutouts
python3 avatar/pack_sprites.py eggman
python3 avatar/tayne/export_preview.py --character eggman --size 256
```

Use `--source-start SECONDS` for a trimmed input, or `--clip chew` to extract one sequence. `--qa` optionally saves the original crops and full-resolution transparent cutouts for inspection. The video and audio are not included in the repository.

### Front-reveal source comparisons

Both clips are now included in the runtime manifest and packed firmware: the close-up is startup, and the wider lowering shot is error and power off. The original comparison previews remain below. Both preserve consecutive filmed samples at 15 fps, with the same background matte and 64×64 output as the existing art.

| Clip | Source segment | Samples | Preview |
| --- | --- | --- | --- |
| Front lowering, wider shot | 1:43.85–1:45.58 | 26 | [Pants lower from neutral to the front reveal](avatar/eggman/candidates/front-lower.gif) |
| Front reveal, close-up | 1:50.40–1:52.00 | 24 | [Starts revealed, pulls pants up, returns to neutral](avatar/eggman/candidates/front-reveal.gif) |

Startup has 1.8 seconds to show its 1.6-second clip. Power off has 2.2 seconds: the full 26-frame lowering sequence plays at 15 fps, followed by a 0.35-second fade. Other characters retain Muse’s original 1.4-second startup and 1.5-second shutdown timings.

The wider shot contains the actual lowering motion; the close-up begins with the pants already down. They remain separate clips, without reversing frames, inventing a transition, or joining the camera angles. The previews repeat for comparison; these excerpts are not seamless loops. GIFs show the RGB565-converted pixels enlarged with nearest-neighbor scaling.

The separate [comparison manifest](avatar/eggman/candidates/source-clips.json) records the exact crops and timing. Reproduce the sheets and previews with:

```sh
python3 avatar/eggman/extract_video.py /path/to/eggman.mp4 \
  --spec avatar/eggman/candidates/source-clips.json \
  --output avatar/eggman/candidates --preview --qa /tmp/eggman-candidates
```

The Apache license covers the code, not the source-video images or third-party character, likeness, and trademark rights. This is an unofficial fan project with no endorsement by the sketch's creators or rights holders. See [NOTICE](NOTICE).
