import os
from aiohttp import web
from folder_paths import get_directory_by_type
from server import PromptServer

routes = PromptServer.instance.routes


@routes.get("/ig1api/images")
async def get_images(request: web.Request) -> web.Response:
    input_dir = get_directory_by_type("input")
    input_images = sorted(
        (entry for entry in os.scandir(input_dir) if entry.is_file()),
        key=lambda entry: -entry.stat().st_mtime
    )
    input_names = [entry.name for entry in input_images]

    output_dir = get_directory_by_type("output")
    output_images = sorted(
        (entry for entry in os.scandir(output_dir) if entry.is_file()),
        key=lambda entry: -entry.stat().st_mtime
    )
    output_names = [entry.name + " [output]" for entry in output_images]

    return web.json_response(input_names + output_names, status=200)


def run_api_server():
    print("IG1 API Server started")
