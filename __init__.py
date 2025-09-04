# pylint: disable=missing-module-docstring,invalid-name
from .fluxresolution import FluxResolution

NODE_CLASS_MAPPINGS = {
    "FluxResolution": FluxResolution,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxResolution": "Flux Resolution",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
