from .helpers import Resolution, generate_all_valid_resolutions

PATCH_LEN = 16
MIN_LEN = 320
# max training size, ~1MP pixels. Model can handle up to ~2M pixels which will reach with 2x HiRes fix.
MAX_SIZE = 1024 * 1024


# Precompute all valid resolutions
all_valid_resolutions = generate_all_valid_resolutions(
    PATCH_LEN, MIN_LEN, MAX_SIZE)


def get_best_valid_resolution(res: Resolution) -> Resolution:
    # Is the resolution already valid?
    if res.valid(patch_len=PATCH_LEN, min_len=MIN_LEN, max_size=MAX_SIZE):
        return res
    # Find the best one
    return all_valid_resolutions.get_best_candidate(res)
