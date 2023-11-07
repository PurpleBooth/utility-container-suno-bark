FROM ubuntu:22.04 as base
ARG TARGETPLATFORM

# Create run user
RUN mkdir -vp /home/ubuntu/app/src \
    && groupadd -g 568 ubuntu \
    && useradd -rm -d /home/ubuntu -s /bin/bash --gid ubuntu -u 568 ubuntu \
    && chown -vR ubuntu:ubuntu /home/ubuntu

# Create make "add-apt-repository" work
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common \
    && rm -vrf /var/lib/apt/lists/* \
    && apt-get clean

# Install python
RUN add-apt-repository ppa:deadsnakes/ppa -y  \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip python3-venv wget python3.11-full \
    && rm -vrf /var/lib/apt/lists/* \
    && apt-get clean

# Install cuda
RUN wget "https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/$(case "$TARGETPLATFORM" in "linux/amd64") echo "x86_64"; ;; "linux/arm64") echo "arm64"; ;; *) exit 99; ;; esac)/cuda-keyring_1.1-1_all.deb" \
    && dpkg -i cuda-keyring_1.1-1_all.deb \
    && rm -v cuda-keyring_1.1-1_all.deb \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y cuda-toolkit libcudnn8 libcudnn8-dev libnccl2 libnccl-dev \
    && rm -vrf /var/lib/apt/lists/* \
    && apt-get clean

# Setup predictable cache directories, that users can overwrite etc
RUN mkdir -vp "/poetry-cache" "/cache" && chown -vR 568:568 "/poetry-cache" "/cache"
ENV POETRY_CACHE_DIR="/poetry-cache"

# Switch to user
WORKDIR /home/ubuntu/app
USER ubuntu

# Install Poetry
ENV PATH="/home/ubuntu/.local/bin:${PATH}"
RUN python3 -m pip install --user --upgrade pip pipx
RUN python3 -m pipx install poetry

# Add the app
COPY poetry.lock pyproject.toml /home/ubuntu/app/
RUN mkdir -vp "/home/ubuntu/app/src" \
    && touch /home/ubuntu/app/src/main.py \
    && poetry install \
    && rm -v /home/ubuntu/app/src/main.py
COPY src/main.py /home/ubuntu/app/src

# Now we are ready to go, override the caches to be the user ones
ENV XDG_CACHE_HOME=/cache
ENV NLTK_DATA=/cache

# Run command
ENTRYPOINT ["poetry", "run", "python3", "src/main.py"]
CMD ["--help"]