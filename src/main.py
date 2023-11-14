import os
import shlex
import string
import subprocess
from functools import lru_cache
from tempfile import NamedTemporaryFile
from typing import Annotated, Optional

import nltk
import numpy as np
import requests
import torch
import typer
from bark import SAMPLE_RATE, generate_audio, preload_models, save_as_prompt
from rich.progress import Progress
from scipy.io.wavfile import write as write_wav
from typer import Argument, FileBinaryWrite, Option

cached_generate_audio = lru_cache(maxsize=1024)(generate_audio)


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
    with Progress() as progress:
        task = progress.add_task("Loading models", total=2)
        preload_models(
            text_use_gpu=torch.cuda.is_available(),
            coarse_use_gpu=torch.cuda.is_available(),
            fine_use_gpu=torch.cuda.is_available(),
            codec_use_gpu=torch.cuda.is_available(),
        )
        progress.update(task, advance=1)
        nltk.download("punkt", quiet=True)
        progress.update(task, advance=1)

        if source_text_file.startswith("http:") or source_text_file.startswith(
            "https:"
        ):
            task = progress.add_task("Downloading text", total=1)
            response = requests.get(source_text_file, timeout=60)
            response.raise_for_status()
            text_prompt = response.text.strip()
            progress.update(task, advance=1)
        else:
            with open(source_text_file, "r") as f:
                text_prompt = f.read().strip()

        task = progress.add_task("Preprocessing text", total=1)
        sentences = pre_process_text(text_prompt)
        progress.update(task, advance=1)

        silence = np.zeros(int(0.1 * SAMPLE_RATE))  # tenth of a second of silence

        if voice_prompt is not None:
            task = progress.add_task("Generating voice from prompt", total=1)
            prompt_file = NamedTemporaryFile(suffix=".npz")
            (full_generation, _) = generate_audio(
                voice_prompt, silent=True, output_full=True
            )
            save_as_prompt(prompt_file.name, full_generation)
            voice_preset = prompt_file.name
            progress.update(task, advance=1)

        pieces = []

        task = progress.add_task("Generating audio", total=len(sentences))
        for sentence in sentences:
            audio_array = cached_generate_audio(
                sentence, history_prompt=voice_preset, silent=True
            )
            pieces += [audio_array, silence.copy()]
            progress.update(task, advance=1)

        wav_path = f"{destination_file.name}.wav"
        write_wav(wav_path, SAMPLE_RATE, np.concatenate(pieces).flatten())

        if os.path.exists(destination_file.name):
            os.unlink(destination_file.name)

        task = progress.add_task("Denoising", total=1)
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
        progress.update(task, advance=1)


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


@lru_cache(maxsize=1024)
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


@lru_cache(maxsize=1024)
def count_syllables_in_phrase_roughly(phrase: str) -> int:
    return sum(
        map(count_syllables_in_word_roughly, phrase.replace("\n", " ").split(" "))
    )


@lru_cache(maxsize=1024)
def count_syllables_in_word_roughly(word: str) -> int:
    ssp = nltk.SyllableTokenizer()
    return len(ssp.tokenize(word))


if __name__ == "__main__":
    typer.run(main)
