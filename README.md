# ComfyUI Flux Resolution

This repository contains ComfyUI nodes that help in determining the closest compatible flux resolution for a given input resolution.

## Installation

### Manual

1. Either clone this repository or download the ZIP and extract it into your `custom_nodes` directory of ComfyUI.

2. Restart ComfyUI to load the new node.

### ComfyUI Manager

1. Open ComfyUI Manager.
2. Click on "Install via Git URL".
3. Enter the following URL: `https://github.com/iguanesolutions/comfyui-flux-resolution.git`.

## Usage

Once installed, you will find a new node called "Flux Resolution" under the "flux tools" category.

It is designed to take an input resolution and output the closest compatible flux resolution and a boolean that tells if the final image needs to be upscaled or not.

In order to use it properly you will need some extra nodes from [ComfyUI Essentials](https://github.com/cubiq/ComfyUI_essentials) and [Crystools](https://github.com/crystian/ComfyUI-Crystools) and an upscale model (like [RealESRGAN_x4plus](https://openmodeldb.info/models/4x-realesrgan-x4plus) or anything else that works for you).

This will let you do conditional resize of the output.

### Examples

![upscale](example_upscale.png)

![downscale](example_downscale.png)

[Workflow](example_workflow.json)
