# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
from comfy_api.latest import io

from .tools import Resolution, get_flux_closest_valid_resolution

HIRES_RATIO = 2


class FluxResolution(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="FluxResolution",
            display_name="Flux Resolution",
            category="Flux tools",
            description=f"""From a user input desired resolution, this node will compute:
- A (adjusted if necessary) reference resolution the closest possible from the input resolution but respecting the flux stepping (should be 32 but we found 16 works well and offers is more flexible for first pass resolutions)
- A first generation pass, flux compatible, resolution for the first sampling based on the reference resolution but also respecting minimal and maximal resolution
- A boolean indicating if a second pass {HIRES_RATIO}x upscale (HiRes fix recommended) is necessary, aka if the generate resolution is lower than the reference resolution
- A boolean indicating if a third pass (pure upscale) is necessary, aka if the the size post 2nd pass (doubling the resolution) is still under the reference resolution
""",
            inputs=[
                io.Int.Input(
                    "desired_width",
                    min=32,
                    display_mode=io.NumberDisplay.number,
                ),
                io.Int.Input(
                    "desired_height",
                    min=32,
                    display_mode=io.NumberDisplay.number,
                )
            ],
            outputs=[
                io.Int.Output(
                    "reference_width",
                    tooltip="The adjusted (stepping) reference width. The Flux generate width will be based on it. Use it for final downscale if any post generation upscale phases are needed."
                ),
                io.Int.Output(
                    "reference_height",
                    tooltip="The adjusted (stepping) reference height. The Flux generate height will be based on it. Use it for final downscale if any post generation upscale phases are needed."
                ),
                io.Int.Output(
                    "generate_width",
                    tooltip="The first pass Flux generation resolution respecting Flux min and max width sizes."
                ),
                io.Int.Output(
                    "generate_height",
                    tooltip="The first pass Flux generation resolution respecting Flux min and max height sizes."
                ),
                io.Boolean.Output(
                    "hires_upscale",
                    tooltip=f"Indicate if a second pass, {HIRES_RATIO}x HiRes upscale is needed. True if the generate resolution is lower than the reference resolution."
                ),
                io.Boolean.Output(
                    "additional_upscale",
                    tooltip="Indicate if a third pass, regular upscale is needed. True if the HiRes second phase resolution is lower than the reference resolution."
                )
            ],
        )

    @classmethod
    def execute(cls, width, height) -> io.NodeOutput:
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
        # Return to the user everything he needs for next steps
        return io.NodeOutput(
            adjusted_ref_reso.width, adjusted_ref_reso.height,
            flux_reso.width, flux_reso.height,
            need_hires,
            need_upscale,
        )
