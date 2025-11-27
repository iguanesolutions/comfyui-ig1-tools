from .helpers import Resolution, generate_all_valid_resolutions

PATCH_LEN = 16
MIN_LEN = 400  # is and must be dividable by PATCH_LEN
# We do not know max training size. But for flux 1 training was 1mp (1024*1024) and model able to do 2mp.
# Here BFL is saying that the model is capable of generating 4mp output images. Let's deduce training was up to 2mp (~1414x1414)
MAX_SIZE = 2000000


# Precompute all valid resolutions
all_valid_resolutions = generate_all_valid_resolutions(
    PATCH_LEN, MIN_LEN, MAX_SIZE)


def get_best_valid_resolution(res: Resolution) -> Resolution:
    # Is the resolution already valid?
    if res.valid(patch_len=PATCH_LEN, min_len=MIN_LEN, max_size=MAX_SIZE):
        return res
    # Find the best one
    return all_valid_resolutions.get_best_candidate(res)
