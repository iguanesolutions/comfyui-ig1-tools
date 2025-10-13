# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
from .helpers import Resolution, generate_all_valid_resolutions

PATCH_LEN = 8  # VAE related
MIN_LEN = 512
# max training size, ~1MP pixels
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
