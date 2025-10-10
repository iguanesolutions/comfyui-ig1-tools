# pylint: disable=missing-module-docstring,disable=missing-class-docstring,missing-function-docstring,line-too-long
from comfy_api.latest import io
import requests

models = ["flux-1-dev", "flux-1-kontext-dev", "flux-tools", "flux-1-krea-dev"]


class FluxReport(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="IG1FluxReport",
            display_name="Flux Licensing Usage Report",
            category="Flux Tools",
            description=f"A simple passthru node that report the number of generated image(s) to Black Forest Labs. Usefull only when you are generating images for commercial use. See https://bfl.ai/licensing and https://docs.bfl.ai/api-reference/models/report-model-usage",
            inputs=[
                io.Image.Input(
                    "image",
                    display_name="image",
                    tooltip="The generated image(s) with the Flux model. The batched will be counted to report the correct number of generated images.",
                ),
                io.Combo.Input(
                    "model",
                    options=models,
                    display_name="FLUX model",
                    tooltip="The licensed model your want to report usage for.",
                    default=models[0]
                ),
                io.String.Input(
                    "api_key",
                    display_name="API Key",
                    tooltip="Your Black Forest Labs API Key for usage reporting.",
                    default="",
                )
            ],
            outputs=[
                io.Image.Output(
                    "output_image",
                    display_name="IMAGE",
                    tooltip="The untouched, passed thru, input image(s).",
                ),
            ],
        )

    @classmethod
    def execute(cls, image, model, api_key) -> io.NodeOutput:
        try:
            response = requests.post(
                f"https://api.bfl.ai/v1/licenses/models/{model}/usage",
                headers={"x-key": api_key},
            )
            response.raise_for_status()
            print(
                f"Successfully reported {len(image)} image(s) to Black Forest Labs for {model}")
        except requests.exceptions.RequestException as e:
            raise Exception(
                f"Failed to report images to Black Forest Labs: {e}")
        return io.NodeOutput(image)

    @classmethod
    def validate_inputs(cls, model, api_key) -> bool | str:
        print(f"validation method called: {model}, '{api_key}'")
        if model not in models:
            return f"Invalid model '{model}', valid models are {models}"
        if api_key == "":
            return "The API key can not be empty"
        return True
