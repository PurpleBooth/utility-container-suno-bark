FROM ubuntu:22.04 as base

RUN groupadd -g 568 ubuntu \
    && useradd -rm -d /home/ubuntu -s /bin/bash --gid ubuntu -u 568 ubuntu

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN add-apt-repository ppa:deadsnakes/ppa -y  \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip python3-venv wget python3.11-full \
    && rm -rf /var/lib/apt/lists/*

RUN wget "https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb" \
    && dpkg -i cuda-keyring_1.1-1_all.deb \
    && rm cuda-keyring_1.1-1_all.deb \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y cuda-toolkit libcudnn8 libcudnn8-dev libnccl2 libnccl-dev \
    && rm -rf /var/lib/apt/lists/*


RUN mkdir -vp "/home/ubuntu/app/src"
WORKDIR /home/ubuntu/app
USER ubuntu
ENV PATH="/home/ubuntu/.local/bin:${PATH}"
RUN python3 -m pip install --user --upgrade pip pipx
RUN python3 -m pipx install poetry

COPY --chown=ubuntu:ubuntu poetry.lock pyproject.toml /home/ubuntu/app/
RUN poetry install
COPY --chown=ubuntu:ubuntu src/main.py /home/ubuntu/app/src

# Warm up downloadables
RUN echo hello | poetry run python3 src/main.py /dev/stdin /dev/null

ENTRYPOINT ["poetry", "run", "python3", "src/main.py"]
CMD ["--help"]