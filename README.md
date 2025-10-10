# ComfyUI Flux Tools

This repository contains ComfyUI nodes to assist Flux generation workflow in ComfyUI.

## Installation

### Manual

1. Either clone this repository or download the ZIP and extract it into your `custom_nodes` directory of ComfyUI.
2. Restart ComfyUI to load the new node.

### ComfyUI Manager

1. Open ComfyUI Manager.
2. Click on "Install via Git URL".
3. Enter the following URL: `https://github.com/iguanesolutions/comfyui-flux-tools.git`.

## Usage

Once installed, you will find the following nodes under the `Flux Tools` category:

* `Flux Resolution`
* `Flux Licensing Usage Report`

### Flux Resolution

This node takes a desired resolution and computes the closest valid resolution for Flux generation, including whether a HiRes fix is needed and a final upscale is needed.

Example:
1. Input resolution is `3844x2160`. The resolution is not valid because:
    1. It does not respect the flux stepping
    2. It is over the max size
2. The first computation will be to compute a resolution respecting the stepping (we use 16 instead of 32 more information below). The closest valid resolution will be computed: `3844x2160` -> `3840x2160`. This resolution will be the "reference" resolution, used for further computation and can (should) also be used as the final downscale target resolution to keep the generated image ratio.
3. The second computation will be the generate resolution: based on the reference resolution, we will compute a new resolution that respect the minimum and maximum size for the Flux model. Use it for the first pass generation (from scratch/noise). In our example the generate resolution will be `1280x720`.
4. Because the reference resolution `3840x2160` is bigger than the generate resolution, the `hires_upscale` boolean will be set to true: it indicates that a second pass is needed to upscale the image to the reference resolution. We recommended to not perform a simple upscale but a 2x HiRes fix on this step.
5. Because the HiRes fix will upscale (and add details to) the image to `2560x1440` (x2) and this resolution is still under the reference resolution, the `additional_upscale` boolean will be set to true: it indicates that a third pass is needed to upscale the image to the reference resolution. We recommended to perform a simple upscale on this step.
6. By upscaling the hires image by x2 again we will optain a final image of `5120x2880` that is bigger than the reference resolution, at this step a downscale will be needed to get the final image to the reference resolution of `3840x2160`.

By using conditionnal nodes on your workflow you can acheive a fully automated workflow that:

1. Take any desired width and height as input
2. Compute the optimal generate resolution for Flux
3. Perform if necessary a second HiRes pass
4. Perform if necessary an additionnal upscale pass
5. Downscale the image if needed
6. Output the final image to the reference resolution (or even the user input size if it is okay for you to take the risk to crop/fill the image).

Check the example below !

> [!NOTE]
> Original stepping for Flux Dev is 32 (as indicated by the [API parameters](https://docs.bfl.ai/api-reference/tasks/generate-an-image-with-flux1-[dev]#body-width)). But we use a 16 stepping to allow more flexibility on the final image size.
> For example for a 16/9 ratio, with a 32 stepping and a 1440 max size, the biggest generate resolution would be 1024x576. With a 16 stepping, the biggest generate resolution can be 1280x720. During our tests, we noticed that the 16 stepping did not introduced any artifacts on the final image while providing more granularity for the generate resolution yielding better results thanks to bigger generate resolutions.

### Flux Licensing Usage Report

This nodes allows you to seamlessly report your generation to Black Forest Labs if you have a licensed Flux Dev model. It supports multi images batches too.

Check the example below !

## Example

![workflow_screenshot](res/flux_hires_generate.png)

You can [download](res/flux_hires.json) the example workflow to test an automatic Flux HiRes generation. You will need 2 additionals custom nodes to run it:

* [ComfyUI Essentials](https://github.com/cubiq/ComfyUI_essentials)
* [Crystools](https://github.com/crystian/ComfyUI-Crystools)
