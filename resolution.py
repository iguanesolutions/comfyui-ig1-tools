# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
from comfy_api.latest import io, ui

from .helpers import Resolution

ResolutionParam = io.Custom("IG1_RESOLUTION")


class ResolutionPacker(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="IG1Resolution",
            display_name="Resolution",
            category="IG1 Tools",
            description=f"""Pack a width and height as resolution""",
            inputs=[
                io.Int.Input(
                    "width",
                    tooltip="The resolution width",
                    min=1,
                    default=3840,  # 4k
                    max=7680,  # 8k
                    display_mode=io.NumberDisplay.number,
                ),
                io.Int.Input(
                    "height",
                    tooltip="The resolution height",
                    min=1,
                    default=2160,  # 4k
                    max=4320,  # 8k
                    display_mode=io.NumberDisplay.number,
                )
            ],
            outputs=[
                ResolutionParam.Output(
                    "resolution",
                    "RESOLUTION",
                    tooltip="The packed resolution",
                )
            ],
        )

    @classmethod
    def execute(cls, width, height) -> io.NodeOutput:
        res = Resolution(width, height)
        return io.NodeOutput(
            res,
            ui=ui.PreviewText(value=res.aspect_ratio().__str__()),
        )


class ResolutionProperties(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="IG1ResolutionProperties",
            display_name="Resolution Properties",
            category="IG1 Tools",
            description=f"""Extract""",
            inputs=[
                ResolutionParam.Input(
                    "resolution",
                    tooltip="The packed resolution",
                )
            ],
            outputs=[
                io.Int.Output(
                    "width",
                    display_name="WIDTH",
                    tooltip="The resolution width",
                ),
                io.Int.Output(
                    "height",
                    display_name="HEIGHT",
                    tooltip="The resolution height",
                ),
                io.Int.Output(
                    "ratio_numerator",
                    display_name="RATIO_NUMERATOR",
                    tooltip="The resolution ratio numerator",
                ),
                io.Int.Output(
                    "ratio_denominator",
                    display_name="RATIO_DENOMINATOR",
                    tooltip="The resolution ratio denominator",
                ),
                io.Float.Output(
                    "ratio_value",
                    display_name="RATIO_VALUE",
                    tooltip="The resolution ratio value",
                )
            ],
        )

    @classmethod
    def execute(cls, resolution: Resolution) -> io.NodeOutput:
        ratio = resolution.aspect_ratio()
        return io.NodeOutput(
            resolution.width, resolution.height,
            ratio.numerator, ratio.denominator, ratio.value(),
        )
