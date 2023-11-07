from tempfile import mktemp
from typing import Annotated

import nltk
import numpy as np
import torch
import typer
from bark import SAMPLE_RATE, generate_audio, preload_models, save_as_prompt
from scipy.io.wavfile import write as write_wav
from tqdm import tqdm
from typer import Argument, FileBinaryWrite, FileText


def main(
    source_text_file: Annotated[
        FileText, typer.Argument(..., file_okay=True, exists=True)
    ],
    destination_wav_file: Annotated[FileBinaryWrite, Argument(...)],
) -> None:
    nltk.download("punkt")
    preload_models(
        text_use_gpu=torch.cuda.is_available(),
        coarse_use_gpu=torch.cuda.is_available(),
        fine_use_gpu=torch.cuda.is_available(),
        codec_use_gpu=torch.cuda.is_available(),
    )

    text_prompt = " ".join(source_text_file.readlines()).strip()

    sentences = nltk.sent_tokenize(text_prompt)
    silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

    temp_file = mktemp(suffix=".npz")
    history = None
    pieces = []
    for sentence in tqdm(sentences, unit="sentence"):
        (full_generation, audio_array) = generate_audio(sentence, history_prompt=history, output_full=True)

        save_as_prompt(temp_file, full_generation)
        history = temp_file
        pieces += [audio_array, silence.copy()]

    write_wav(destination_wav_file, SAMPLE_RATE, np.concatenate(pieces))


if __name__ == "__main__":
    typer.run(main)
