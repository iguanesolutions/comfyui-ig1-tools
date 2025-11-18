import folder_paths
import node_helpers

import numpy as np
import torch

from PIL import Image, ImageOps, ImageSequence

from comfy_api.latest import io


class LoadImage(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="IG1LoadImage",
            display_name="Load input/output image",
            category="IG1 Tools",
            description=f"""Load an image from input/output folders.""",
            is_experimental=True,
            inputs=[
                io.Combo.Input(
                    "image",
                    upload=io.UploadType.image,
                    image_folder=io.FolderType.input,
                    remote=io.RemoteOptions(
                        route="/ig1api/images",
                        refresh_button=True,
                        control_after_refresh="first",
                    ),
                ),
            ],
            outputs=[io.Image.Output(
                "output_image",
            ), io.Mask.Output(
                "output_mask",
            )],
        )

    @classmethod
    def execute(cls, image) -> io.NodeOutput:
        image_path = folder_paths.get_annotated_filepath(image)

        img = node_helpers.pillow(Image.open, image_path)

        output_images = []
        output_masks = []
        w, h = None, None

        excluded_formats = ['MPO']

        for i in ImageSequence.Iterator(img):
            i = node_helpers.pillow(ImageOps.exif_transpose, i)

            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")

            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]

            if image.size[0] != w or image.size[1] != h:
                continue

            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            elif i.mode == 'P' and 'transparency' in i.info:
                mask = np.array(i.convert('RGBA').getchannel(
                    'A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, output_mask)
