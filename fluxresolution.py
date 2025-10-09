# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
from comfy.comfy_types import IO
from server import PromptServer
from .tools import Resolution, get_flux_closest_valid_resolution

HIRES_RATIO = 2


class FluxResolution():
    CATEGORY = "flux tools"
    RETURN_TYPES = (
        IO.INT, IO.INT,
        IO.INT, IO.INT,
        IO.BOOLEAN,
        IO.BOOLEAN,
    )
    RETURN_NAMES = (
        "reference_width", "reference_height",
        "generate_width", "generate_height",
        "need_hires",
        "need_final_upscale",
    )
    FUNCTION = "run"
    DESCRIPTION = """From a user input desired resolution, this node will compute:
- A (adjusted if necessary) reference resolution the closest possible from the input resolution but respecting the flux stepping (should be 32 but we found 16 works well and offers is more flexible for first pass resolutions)
- A first generation pass, flux compatible, resolution for the first sampling based on the reference resolution but also respecting minimal and maximal resolution
- A boolean indicating if a second pass 2x upscale (hires fix recommended) is necessary, aka if the generate resolution is lower than the reference resolution
- A boolean indicating if a third pass (pure upscale) is necessary, aka if the the size post 2nd pass (doubling the resolution) is still under the reference resolution
"""

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
        pass

    def run(self, width, height, unique_id=None) -> tuple[int, int, int, int, bool, bool]:
        # Compute the flux first pass generation resolution
        # and the adjusted (if necessary) reference resolution.
        flux_reso, adjusted_ref_reso = get_flux_closest_valid_resolution(
            Resolution(width, height)
        )
        # Compute if a HiRes fix x2 second pass is needed to get to the reference resolution
        need_hires = False
        need_upscale = False
        if flux_reso.width < adjusted_ref_reso.width or flux_reso.height < adjusted_ref_reso.height:
            need_hires = True
            hires = Resolution(
                width=flux_reso.width * HIRES_RATIO,
                height=flux_reso.height * HIRES_RATIO
            )
            # And if a 3rd pass pure upscale is necessary post hires fix
            if hires.width < adjusted_ref_reso.width or hires.height < adjusted_ref_reso.height:
                need_upscale = True
        # send debug info to front
        if unique_id:
            debug = f"Input resolution: f{width}×f{height}"
            if width != adjusted_ref_reso.width or height != adjusted_ref_reso.height:
                debug += f"\nAdjusted reference resolution: f{adjusted_ref_reso.width}×f{adjusted_ref_reso.height}"
            debug += f"\nFlux generation resolution: f{flux_reso.width}×f{flux_reso.height}"
            if need_hires:
                debug += "\nSecond pass, 2x HiRes fix"
                if need_upscale:
                    debug += "and third pass final upscale are"
                else:
                    debug += " is"
                debug += " necessary"
            PromptServer.instance.send_progress_text(debug, unique_id)
        # Return to the user everything he needs for next steps
        return adjusted_ref_reso.width, adjusted_ref_reso.height, flux_reso.width, flux_reso.height, need_hires, need_upscale
