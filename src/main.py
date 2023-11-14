import os
import shlex
import string
import subprocess
from functools import cache
from tempfile import NamedTemporaryFile
from typing import Annotated, Optional

import nltk
import numpy as np
import requests
import torch
import typer
from bark import SAMPLE_RATE, generate_audio, preload_models, save_as_prompt
from scipy.io.wavfile import write as write_wav
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
    voice_prompt: Annotated[
        Optional[str],
        Option(
            ...,
            help="This will override any voice preset",
        ),
    ] = None,
    voice_preset: Annotated[
        Optional[str],
        Option(
            ...,
            help="Voice preset, could be one of the built in ones or a path to a saved history",
        ),
    ] = "v2/en_speaker_9",
) -> None:
    preload_models(
        text_use_gpu=torch.cuda.is_available(),
        coarse_use_gpu=torch.cuda.is_available(),
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

    sentences = pre_process_text(text_prompt)

    silence = np.zeros(int(0.1 * SAMPLE_RATE))  # tenth of a second of silence

    if voice_prompt is not None:
        prompt_file = NamedTemporaryFile(suffix=".npz")
        (full_generation, _) = generate_audio(
            voice_prompt, silent=True, output_full=True
        )
        save_as_prompt(prompt_file.name, full_generation)
        voice_preset = prompt_file.name

    pieces = []
    with typer.progressbar(
        sentences,
        label="Generating audio",
        show_eta=True,
        show_percent=True,
        show_pos=True,
    ) as sentences_with_progress:
        for sentence in sentences_with_progress:
            audio_array = generate_audio(
                sentence, history_prompt=voice_preset, silent=True
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


def pre_process_text(text_prompt: str) -> list[str]:
    sentences = nltk.sent_tokenize(text_prompt)
    grouped_sentences: list[str] = [""]
    while len(sentences) > 0:
        # If we have gone over the rough syllable limit start a new chunk
        if count_syllables_in_phrase_roughly(grouped_sentences[-1]) > 30:
            grouped_sentences.append("")
            continue

        if len(grouped_sentences[-1]) > 0:
            grouped_sentences[-1] += " "

        # handling the case where the sentence is too long
        current = sentences.pop(0)
        split_text = [current]

        if count_syllables_in_phrase_roughly(current) > 30:
            # if the sentence is too long, split it into phrases
            split_text = split_phrase(current)

        grouped_sentences[-1] += split_text.pop(0)
        while len(split_text) > 0:
            grouped_sentences.append(
                split_text.pop(0)
            )  # force a break here for the next sense

    return grouped_sentences


@cache
def split_phrase(phrase: str) -> list[str]:
    words = nltk.word_tokenize(phrase)
    new = [""]

    while len(words) > 0:
        word = words.pop(0)

        if len(word) == 1 and word in string.punctuation:
            new[-1] += word
            continue

        if count_syllables_in_phrase_roughly(new[-1]) > 30:
            new.append("")

        new[-1] += " "
        new[-1] += word
        new[-1] = new[-1].strip()

    return new


@cache
def count_syllables_in_phrase_roughly(phrase: str) -> int:
    return sum(
        map(count_syllables_in_word_roughly, phrase.replace("\n", " ").split(" "))
    )


@cache
def count_syllables_in_word_roughly(word: str) -> int:
    ssp = nltk.SyllableTokenizer()
    return len(ssp.tokenize(word))


if __name__ == "__main__":
    typer.run(main)
