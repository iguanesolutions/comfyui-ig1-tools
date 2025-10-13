from typing import Tuple

from .helpers import Resolution, generate_all_valid_resolutions

# Constants
PATCH_LEN = 16    # Should be 32 but it's too limiting; 16 allows for more resolutions and seems to work fine with Flux anyway
MIN_LEN = 320
MAX_SIZE = 1024 * 1024  # max training size


# Precompute all valid resolutions
all_valid_resolutions = generate_all_valid_resolutions(
    PATCH_LEN, MIN_LEN, MAX_SIZE)


def get_closest_valid_resolution(res: Resolution) -> Tuple[Resolution, Resolution]:
    """
    Returns the closest FLUX-compatible resolution and the adjusted reference.
    """
    # Is the resolution already valid?
    if res.valid(patch_len=PATCH_LEN, min_len=MIN_LEN, max_size=MAX_SIZE):
        return res, res
    # Try to find a valid resolution with the same aspect ratio
    candidates = all_valid_resolutions.get_all_with_ratio(res.aspect_ratio())
    if candidates.resolutions:
        return res, candidates.get_closest_equal_or_larger(res)
    # Try with a slight adjustment of the resolution to fit step increments
    adjusted_reference = res.get_closest_valid_patch_resolution(PATCH_LEN)
    if adjusted_reference.valid(patch_len=PATCH_LEN, min_len=MIN_LEN, max_size=MAX_SIZE):
        return adjusted_reference, adjusted_reference
    # As last resort, find the closest valid resolution by aspect ratio
    return adjusted_reference, all_valid_resolutions.get_closest_by_ratio(adjusted_reference)
