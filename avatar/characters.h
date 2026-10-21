#pragma once
#include <stdbool.h>

/* Keep existing indices stable; new characters follow the original default pet. */
enum { MUSE_CHARACTER_DEFAULT = 3, MUSE_CHARACTER_EGGMAN = 4 };

/* Optional custom-avatar roster. Menu and renderer call these on the UI task. */
int muse_character_count(void);
int muse_character_current(void);
const char *muse_character_name(int index);
bool muse_character_select(int index);

/* Full filmed transitions plus a short final hold/fade. Other pets retain
 * the SDK's original startup and shutdown durations. */
static inline int muse_character_boot_ms(int index)
{
    return index == MUSE_CHARACTER_EGGMAN ? 1800 : 1400;
}
static inline int muse_character_off_ms(int index)
{
    return index == MUSE_CHARACTER_EGGMAN ? 2200 : 1500;
}
