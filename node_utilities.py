# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
from comfy_api.latest import io, ui

from .helpers import Resolution, AspectRatio

ResolutionParam = io.Custom("IG1_RESOLUTION")
RatioParam = io.Custom("IG1_ASPECTRATIO")


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
            description=f"""Extract a resolution properties""",
            inputs=[
                ResolutionParam.Input(
                    "resolution",
                    tooltip="The packed resolution to extract properties from",
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
                RatioParam.Output(
                    "ratio",
                    display_name="ASPECT_RATIO",
                    tooltip="The resolution aspect ratio",
                ),
            ],
        )

    @classmethod
    def execute(cls, resolution: Resolution) -> io.NodeOutput:
        ratio = resolution.aspect_ratio()
        return io.NodeOutput(
            resolution.width, resolution.height, ratio,
        )


class AspectRatioProperties(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="IG1AspectRatioProperties",
            display_name="Aspect Ratio Properties",
            category="IG1 Tools",
            description=f"""Extract an aspect ratio properties""",
            inputs=[
                RatioParam.Input(
                    "aspect_ratio",
                    tooltip="The aspect ratio you want to extract properties from",
                ),
            ],
            outputs=[
                io.Int.Output(
                    "numerator",
                    display_name="NUMERATOR",
                    tooltip="The aspect ratio numerator",
                ),
                io.Int.Output(
                    "denominator",
                    display_name="DENOMINATOR",
                    tooltip="The aspect ratio denominator",
                ),
                io.Float.Output(
                    "value",
                    display_name="VALUE",
                    tooltip="The aspect ratio value",
                )
            ],
        )

    @classmethod
    def execute(cls, aspect_ratio: AspectRatio) -> io.NodeOutput:
        return io.NodeOutput(
            aspect_ratio.numerator, aspect_ratio.denominator, aspect_ratio.value(),
        )
