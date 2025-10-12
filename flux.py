from typing import Tuple

from .tools import AspectRatio, Resolution, ResolutionsList, get_closest_valid_patch_resolution

# Constants
PATCH_SIZE = 16    # Should be 32 but it's too limiting; 16 allows for more resolutions and seems to work fine with Flux anyway
MIN_LEN = 320
MAX_SIZE = 1440


def compute_all_flux_valid_resolutions() -> ResolutionsList:
    valid_resolutions = []

    # Start with one less than the minimum to generate the first candidate below min_size
    width_multiplier = (MIN_LEN // PATCH_SIZE) - 1
    while True:
        width_multiplier += 1
        width = PATCH_SIZE * width_multiplier
        if width > MAX_SIZE:
            break

        # For each width, iterate through height multipliers
        height_multiplier = (MIN_LEN // PATCH_SIZE) - 1
        while True:
            height_multiplier += 1
            height = PATCH_SIZE * height_multiplier
            if height > MAX_SIZE:
                break
            valid_resolutions.append(Resolution(width, height))

    return ResolutionsList(valid_resolutions)


# Precompute all valid resolutions
all_valid_resolutions = compute_all_flux_valid_resolutions()


def get_flux_resolutions_by_ratio(ratio: AspectRatio) -> ResolutionsList:
    valid_resolutions = []
    for res in all_valid_resolutions.resolutions:
        if res.aspect_ratio() == ratio:
            valid_resolutions.append(res)
    return ResolutionsList(valid_resolutions)


def get_flux_closest_valid_resolution(res: Resolution) -> Tuple[Resolution, Resolution]:
    """
    Returns the closest FLUX-compatible resolution and the adjusted reference.
    """
    # Is the resolution already valid?
    if res.valid(patch=PATCH_SIZE, min_size=MIN_LEN, max_size=MAX_SIZE):
        return res, res
    # Try to find a valid resolution with the same aspect ratio
    candidates = get_flux_resolutions_by_ratio(res.aspect_ratio())
    if candidates.resolutions:
        flux_valid = candidates.get_closest_equal_or_larger(res)
        return flux_valid, res
    # Try with a slight adjustment of the resolution to fit step increments
    adjusted_reference = get_closest_valid_patch_resolution(res, PATCH_SIZE)
    if adjusted_reference.flux_valid():
        return adjusted_reference, adjusted_reference
    # As last resort, find the closest valid resolution by aspect ratio
    flux_valid = all_valid_resolutions.get_closest_by_ratio(
        adjusted_reference)
    return flux_valid, adjusted_reference
