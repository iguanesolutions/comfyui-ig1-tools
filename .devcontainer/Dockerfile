FROM mcr.microsoft.com/devcontainers/python:1-3.12
RUN git clone https://github.com/comfyanonymous/ComfyUI --single-branch
WORKDIR /ComfyUI
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
