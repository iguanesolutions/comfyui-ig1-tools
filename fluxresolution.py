# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
from comfy_api.latest import io

from .helpers import Resolution, HIRES_RATIO
from .resolution import ResolutionParam
from .flux import get_flux_closest_valid_resolution


class FluxResolution(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="IG1FluxResolution",
            display_name="Flux Resolution",
            category="IG1 Tools",
            description=f"""From a user input desired resolution, this node will compute:
1. A (adjusted if necessary) reference resolution the closest possible from the input resolution but respecting the flux patch length (should be 32 but we found 16 works well and offers is more flexible for first pass resolutions).
2. A first generation pass, flux compatible, resolution for the first sampling based on the reference resolution but also respecting minimal and maximal resolution.
3. A boolean indicating if a second pass {HIRES_RATIO}x upscale (HiRes fix recommended) is necessary, aka if the generate resolution is lower than the reference resolution.
4. A boolean indicating if a third pass (pure upscale) is necessary, aka if the the size post 2nd pass (doubling the resolution) is still under the reference resolution.
""",
            inputs=[
                ResolutionParam.Input(
                    "resolution",
                    tooltip="The desired resolution of the image to be generated. Will be adjusted as reference to match patch length if necessary.",
                ),
            ],
            outputs=[
                ResolutionParam.Output(
                    "reference",
                    display_name="REFERENCE",
                    tooltip="The adjusted (patch length) reference resolution. The Flux generate resolution will be based on it. Use it for final downscale."
                ),
                ResolutionParam.Output(
                    "generate",
                    display_name="GENERATE",
                    tooltip="The first pass Flux generation resolution respecting Flux min lenghts and max size."

                ),
                io.Boolean.Output(
                    "hires",
                    display_name="NEED_HIRES",
                    tooltip=f"Indicate if a second pass, {HIRES_RATIO}x HiRes upscale is needed. True if the generate resolution is lower than the reference resolution."
                ),
                io.Boolean.Output(
                    "upscale",
                    display_name="NEED_UPSCALE",
                    tooltip="Indicate if a third pass, regular upscale is needed. True if the HiRes second phase resolution is lower than the reference resolution."
                )
            ],
        )

    @classmethod
    def execute(cls, resolution) -> io.NodeOutput:
        # Compute the flux first pass generation resolution
        # and the adjusted (if necessary) reference resolution.
        adjusted_ref_reso, generate_reso = get_flux_closest_valid_resolution(
            resolution)
        # Compute if a HiRes fix x2 second pass is needed to get to the reference resolution
        need_hires = False
        need_upscale = False
        if generate_reso.width < adjusted_ref_reso.width or generate_reso.height < adjusted_ref_reso.height:
            need_hires = True
            hires = Resolution(
                width=generate_reso.width * HIRES_RATIO,
                height=generate_reso.height * HIRES_RATIO
            )
            # And if a 3rd pass pure upscale is necessary post hires fix
            if hires.width < adjusted_ref_reso.width or hires.height < adjusted_ref_reso.height:
                need_upscale = True
        # Return to the user everything he needs for next steps
        return io.NodeOutput(
            adjusted_ref_reso,
            generate_reso,
            need_hires,
            need_upscale,
        )
