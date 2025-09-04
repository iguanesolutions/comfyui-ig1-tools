# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
from typing import List, Tuple
from comfy.comfy_types import IO
from server import PromptServer
from .resolution import AspectRatio, Resolution, ResolutionsList


STEP = 16
MIN_FLUX_PIXELS = 100_000
MAX_FLUX_PIXELS = 2_000_000
COMPATIBILITY_STEP = 64


class FluxResolution():
    CATEGORY = "flux tools"
    RETURN_TYPES = (IO.INT, IO.INT, IO.BOOLEAN)
    RETURN_NAMES = ("width", "height", "upscale")
    FUNCTION = "closest_flux_resolution"
    DESCRIPTION = """Get the closest compatible flux resolution from a given resolution."""

    @classmethod
    def INPUT_TYPES(cls):
        # pylint: disable=invalid-name
        return {
            "required": {
                "width": (IO.INT,),
                "height": (IO.INT,),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    def __init__(self):
        self.minbase = 0
        ratio = 1
        while True:
            self.minbase = STEP * ratio
            if self.minbase * self.minbase > MIN_FLUX_PIXELS:
                break
            ratio += 1

    def closest_flux_resolution(self, width, height, unique_id=None) -> tuple[int, int, bool]:
        res = Resolution(width, height, COMPATIBILITY_STEP)
        flux_res = self.get_flux_closest_valid_resolution(res)
        upscale = res.total_pixels() > MAX_FLUX_PIXELS
        if unique_id:
            input_ratio = res.aspect_ratio()
            output_ratio = flux_res.aspect_ratio()
            if input_ratio != output_ratio:
                txt = f"input aspect ratio: {input_ratio}\noutput aspect ratio: {output_ratio}\nflux resolution: {flux_res}\nupscale: {upscale}"
            else:
                txt = f"aspect ratio: {output_ratio}\nflux resolution: {flux_res}\nupscale: {upscale}"
            PromptServer.instance.send_progress_text(txt, unique_id)
        return flux_res.width, flux_res.height, upscale

    def compute_flux_valid_resolutions(self, ar: AspectRatio) -> ResolutionsList:
        valid_resolutions_list = ResolutionsList()
        width_multiplier, height_multiplier = 0, 0
        ratio = ar.value()
        while True:
            # Compute next width
            width_multiplier += 1
            width = STEP * width_multiplier
            if width < self.minbase:
                continue
            if width * self.minbase > MAX_FLUX_PIXELS:
                break
            # Iterate heights for this width
            height_multiplier = 0
            while True:
                # Compute next height
                height_multiplier += 1
                height = STEP * height_multiplier
                if height < self.minbase:
                    continue
                # If number of pixels is too low, continue to next iteration
                if width * height < MIN_FLUX_PIXELS:
                    continue
                # If we are exceeding the max pixel, no need to perform further checks
                if width * height > MAX_FLUX_PIXELS:
                    break
                # Does this resolution respect the user ratio?
                if width / height != ratio:
                    continue
                # Valid resolution
                valid_resolutions_list.append(
                    Resolution(width, height, COMPATIBILITY_STEP))
        valid_resolutions_list.sort(key=lambda res: res.total_pixels())
        return valid_resolutions_list

    def get_closest_valid_step_resolution(self, res: Resolution) -> Resolution:
        # Integer division to get rounded down values
        truncated_width_ratio = res.width // STEP
        truncated_height_ratio = res.height // STEP
        # Compute candidates resolutions based on the given resolution and the step value
        candidates = ResolutionsList([
            # South West resolution base aligned
            Resolution(truncated_width_ratio * STEP,
                       truncated_height_ratio * STEP, COMPATIBILITY_STEP),
            # North West resolution base aligned
            Resolution(truncated_width_ratio * STEP,
                       (truncated_height_ratio + 1) * STEP, COMPATIBILITY_STEP),
            # South East resolution base aligned
            Resolution((truncated_width_ratio + 1) * STEP,
                       truncated_height_ratio * STEP, COMPATIBILITY_STEP),
            # North East resolution base aligned
            Resolution((truncated_width_ratio + 1) * STEP,
                       (truncated_height_ratio + 1) * STEP, COMPATIBILITY_STEP),
        ])
        return candidates.get_closest(res)

    def get_flux_closest_valid_resolution(self, res: Resolution) -> Resolution:
        # pylint: disable=line-too-long
        # Is the resolution already valid?
        if res.width % STEP == 0 and res.height % STEP == 0 and \
                res.total_pixels() >= MIN_FLUX_PIXELS and res.total_pixels() <= MAX_FLUX_PIXELS:
            return res
        # Res is not valid, let's find the closest one from the same aspect ratio
        candidates = self.compute_flux_valid_resolutions(res.aspect_ratio())
        if candidates:
            # Here we could have used candidates.get_closest(res) but in some cases it would return a smaller resolution than the original one
            # because the lower is closer than the next one which is higher than the ref res. This behavior might be suboptimal for the user:
            # it is better for image to scale down an image than to upscale it.
            return candidates.get_closest_equal_or_larger(res)
        # We cannot keep the resolution nor its aspect ratio, so let's go for a slight ratio change
        closest = self.get_closest_valid_step_resolution(res)
        if closest.total_pixels() > MAX_FLUX_PIXELS:
            return self.compute_flux_valid_resolutions(closest.aspect_ratio()).biggest_resolution()
        if closest.total_pixels() < MIN_FLUX_PIXELS:
            return self.compute_flux_valid_resolutions(closest.aspect_ratio()).smallest_resolution()
        return closest

    def get_resolutions_from_ratio(self, requested_ratio: AspectRatio) -> Tuple[AspectRatio, bool, bool, List[Resolution]]:
        # Let's work with the minimal ratio representation
        ratio = requested_ratio.simplify()
        # First try to generate resolutions with this ratio
        resolutions = self.compute_flux_valid_resolutions(ratio)
        if resolutions:
            simplified_ratio = requested_ratio != ratio
            return ratio, simplified_ratio, False, resolutions
        # We failed to generate any resolutions with this ratio, generate a big enough resolution with this ratio
        big_enough_resolution = Resolution(
            ratio.numerator, ratio.denominator, COMPATIBILITY_STEP)
        # Use it to approach the closest valid resolution and use this resolution's ratio to compute a valid list of resolutions candidates
        adjusted_resolution = self.get_closest_valid_step_resolution(
            big_enough_resolution)
        ratio = adjusted_resolution.aspect_ratio()
        resolutions = self.compute_flux_valid_resolutions(ratio)
        adjusted_ratio = ratio != requested_ratio.simplify()  # should always be true
        return ratio, False, adjusted_ratio, resolutions
