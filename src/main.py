import os
import shlex
import subprocess
from typing import Annotated

import nltk
import numpy as np
import requests
import torch
import typer
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from tqdm import tqdm
from typer import Argument, FileBinaryWrite


def main(
    source_text_file: Annotated[
        str,
        typer.Argument(
            ...,
            help="Text file to use as source for generation, could be a file path or url",
        ),
    ],
    destination_file: Annotated[FileBinaryWrite, Argument(...)],
) -> None:
    preload_models(
        text_use_small=not torch.cuda.is_available(),
        text_use_gpu=torch.cuda.is_available(),
        coarse_use_small=not torch.cuda.is_available(),
        coarse_use_gpu=torch.cuda.is_available(),
        fine_use_small=not torch.cuda.is_available(),
        fine_use_gpu=torch.cuda.is_available(),
        codec_use_gpu=torch.cuda.is_available(),
    )
    nltk.download("punkt")

    if source_text_file.startswith("http:") or source_text_file.startswith("https:"):
        response = requests.get(source_text_file, timeout=60)
        response.raise_for_status()
        text_prompt = response.text.strip()
    else:
        with open(source_text_file, "r") as f:
            text_prompt = f.read().strip()

    sentences = nltk.sent_tokenize(text_prompt)
    silence = np.zeros(int(0.2 * SAMPLE_RATE))  # tenth of a second of silence

    pieces = []
    for sentence in tqdm(sentences, unit="sentence"):
        audio_array = generate_audio(
            sentence, history_prompt="v2/en_speaker_9", silent=True
        )
        pieces += [audio_array, silence.copy()]

    wav_path = f"{destination_file.name}.wav"
    write_wav(wav_path, SAMPLE_RATE, np.concatenate(pieces).flatten())

    if os.path.exists(destination_file.name):
        os.unlink(destination_file.name)

    # note the escaping below
    subprocess.run(
        [  # noqa: S603,S607
            "ffmpeg",
            "-i",
            shlex.quote(wav_path),
            "-af",
            "highpass=f=300,afftdn=nf=-20,dialoguenhance,lowpass=f=3000",
            "-ar",
            shlex.quote(str(SAMPLE_RATE)),
            shlex.quote(destination_file.name),
        ]
    )
    os.unlink(wav_path)


if __name__ == "__main__":
    typer.run(main)
