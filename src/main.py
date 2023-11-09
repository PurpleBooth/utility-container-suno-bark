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
    destination_wav_file: Annotated[FileBinaryWrite, Argument(...)],
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
        text_prompt = requests.get(source_text_file, timeout=60).text.strip()
    else:
        with open(source_text_file, "r") as f:
            text_prompt = f.read().strip()

    sentences = nltk.sent_tokenize(text_prompt)
    silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

    pieces = []
    for sentence in tqdm(sentences, unit="sentence"):
        audio_array = generate_audio(
            sentence, history_prompt="v2/en_speaker_9", silent=True, waveform_temp=0.6
        )
        pieces += [audio_array, silence.copy()]

    write_wav(destination_wav_file, SAMPLE_RATE, np.concatenate(pieces).flatten())


if __name__ == "__main__":
    typer.run(main)
