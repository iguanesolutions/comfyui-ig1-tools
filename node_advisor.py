# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
from comfy_api.latest import io

from .helpers import Resolution, HIRES_RATIO
from .node_utilities import ResolutionParam
from .flux import get_best_valid_resolution as get_flux_best_valid_resolution
from .qwenimage import get_best_valid_resolution as get_qwenimage_best_valid_resolution
from .sdxl import get_best_valid_resolution as get_sdxl_best_valid_resolution

models = ["Qwen-Image", "FLUX.1-dev", "SDXL"]


class ResolutionAdvisor(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="IG1ResolutionAdvisor",
            display_name="Resolution Advisor",
            category="IG1 Tools",
            description=f"""From a user input desired resolution, this node will compute and output:
1. A first generation pass resolution, accounting for model's min len, max size and patch len, with a ratio the closest possible to input resolution.
2. A boolean indicating if a second pass {HIRES_RATIO}x upscale (HiRes fix recommended) is necessary, aka if the generate resolution is lower than the reference resolution.
3. A boolean indicating if a third pass (pure upscale) is necessary, aka if the the size post 2nd pass (doubling the resolution) is still under the reference resolution.
""",
            inputs=[
                ResolutionParam.Input(
                    "resolution",
                    tooltip="The desired resolution of the image to be generated. Will be adjusted as reference to match patch length if necessary.",
                ),
                io.Combo.Input(
                    "model",
                    options=models,
                    default=models[0],
                    tooltip="The model you want to compute advises for. This will be used to get the patch length, min lengths and max size.",
                )
            ],
            outputs=[
                ResolutionParam.Output(
                    "generate",
                    display_name="GENERATE",
                    tooltip="The first pass generation resolution respecting model's patch len, min lenghts and max size."

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
    def execute(cls, resolution, model) -> io.NodeOutput:
        # Compute the flux first pass generation resolution
        # and the adjusted (if necessary) reference resolution.
        if model == "FLUX.1-dev":
            generate_reso = get_flux_best_valid_resolution(resolution)
        elif model == "Qwen-Image":
            generate_reso = get_qwenimage_best_valid_resolution(resolution)
        elif model == "SDXL":
            generate_reso = get_sdxl_best_valid_resolution(resolution)
        else:
            ValueError(f"Model f{model} has no internal configuration.")
        # Compute if a HiRes fix x2 second pass is needed to get to the reference resolution
        need_hires = False
        need_upscale = False
        if generate_reso.width < resolution.width or generate_reso.height < resolution.height:
            need_hires = True
            hires = Resolution(
                width=generate_reso.width * HIRES_RATIO,
                height=generate_reso.height * HIRES_RATIO
            )
            # And if a 3rd pass pure upscale is necessary post hires fix
            if hires.width < resolution.width or hires.height < resolution.height:
                need_upscale = True
        # Return to the user everything he needs for next steps
        return io.NodeOutput(
            generate_reso,
            need_hires,
            need_upscale,
        )
