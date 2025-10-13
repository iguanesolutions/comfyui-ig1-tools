from comfy_api.latest import io

from .helpers import Resolution, ResolutionsList
from .node_utilities import ResolutionParam


# https://github.com/QwenLM/Qwen-Image/issues/7#issuecomment-3153364093
training_resolutions = sorted(
    [
        Resolution(1328, 1328),
        Resolution(1664, 928),
        Resolution(928, 1664),
        Resolution(1472, 1104),
        Resolution(1104, 1472),
        Resolution(1584, 1056),
        Resolution(1056, 1584),
    ],
    key=lambda res: res.total_pixels(),
    reverse=True,
)


class QwenImageNativesResolutions(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="IG1QwenImageNativesResolutions",
            display_name="Qwen Image Natives Resolutions",
            category="IG1 Tools",
            description=f"""This node outputs the list of resolutions that were used in the training of the Qwen Image model. These are the resolutions that are most likely to produce the best results.""",
            inputs=[
                io.Combo.Input(
                    "native_resolution",
                    options=[str(res)
                             for res in training_resolutions],
                    default=str(training_resolutions[0]),
                    tooltip="The model you want to compute advises for. This will be used to get the patch length, min lengths and max size.",
                )
            ],
            outputs=[
                ResolutionParam.Output(
                    "resolution",
                    display_name="RESOLUTION",
                ),
            ],
        )

    @classmethod
    def execute(cls, native_resolution) -> io.NodeOutput:
        # Compute the flux first pass generation resolution
        # and the adjusted (if necessary) reference resolution.
        for res in training_resolutions:
            if str(res) == native_resolution:
                return io.NodeOutput(res)
        raise ValueError(f"Unhandled resolution: {native_resolution}")
