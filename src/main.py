import itertools
import os
import shlex
import string
import subprocess
from tempfile import NamedTemporaryFile
from typing import Annotated, Optional

import nltk
import numpy as np
import requests
import torch
import typer
from bark import SAMPLE_RATE, generate_audio, preload_models, save_as_prompt
from scipy.io.wavfile import write as write_wav
from tqdm import tqdm
from typer import Argument, FileBinaryWrite, Option

def main(
    source_text_file: Annotated[
        str,
        typer.Argument(
            ...,
            help="Text file to use as source for generation, could be a file path or url",
        ),
    ],
    destination_file: Annotated[FileBinaryWrite, Argument(...)],
    voice_prompt: Annotated[Optional[str], Option(...)] = None,
    voice_preset: Annotated[Optional[str], Option(...)] = "v2/en_speaker_9",
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
    ssp = nltk.SyllableTokenizer()

    if source_text_file.startswith("http:") or source_text_file.startswith("https:"):
        response = requests.get(source_text_file, timeout=60)
        response.raise_for_status()
        text_prompt = response.text.strip()
    else:
        with open(source_text_file, "r") as f:
            text_prompt = f.read().strip()

    sentences = pre_process_text(ssp, text_prompt)

    silence = np.zeros(int(0.2 * SAMPLE_RATE))  # fifth of a second of silence

    if voice_prompt is not None:
        prompt_file = NamedTemporaryFile(suffix=".npz")
        (full_generation, _) = generate_audio(
            voice_prompt, silent=True, output_full=True
        )
        save_as_prompt(prompt_file.name, full_generation)
        voice_preset = prompt_file.name

    pieces = []
    for sentence in tqdm(sentences, unit="sentence"):
        audio_array = generate_audio(sentence, history_prompt=voice_preset, silent=True)
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


def pre_process_text(ssp, text_prompt):
    sentences = nltk.sent_tokenize(text_prompt)
    grouped_sentences: list[str] = ['']
    while len(sentences) > 0:
        # If this is a new block, the sentence just drops in there.
        if len(grouped_sentences[-1]) == 0:
            grouped_sentences[-1] = sentences.pop(0)
            continue

        # If we have gone over the rough syllable limit start a new chunk
        if len(ssp.tokenize(grouped_sentences[-1])) > 35:
            grouped_sentences.append('')
            continue

        grouped_sentences[-1] += " "
        grouped_sentences[-1] += sentences.pop(0)
    sentences = grouped_sentences
    return sentences


if __name__ == "__main__":
    typer.run(main)
