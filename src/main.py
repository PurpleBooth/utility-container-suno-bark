import re
from tempfile import NamedTemporaryFile
from typing import Annotated

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
    preload_models(
        text_use_gpu=torch.cuda.is_available(),
        coarse_use_gpu=torch.cuda.is_available(),
        fine_use_gpu=torch.cuda.is_available(),
        codec_use_gpu=torch.cuda.is_available(),
    )

    text_prompt = "\n".join(source_text_file.readlines()).strip()

    sentences = split_and_recombine_text(text_prompt)
    silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

    (full_generation, _) = generate_audio(
        "This is being recorded in a studio.",
        output_full=True,
    )
    temp_file = NamedTemporaryFile(suffix=".npz")
    save_as_prompt(temp_file.name, full_generation)
    history = temp_file.name
    pieces = []
    for sentence in tqdm(sentences, unit="sentence"):
        audio_array = generate_audio(sentence, history_prompt=history)
        pieces += [audio_array, silence.copy()]

    write_wav(destination_wav_file, SAMPLE_RATE, np.concatenate(pieces))


# From tortoise-tts, (Apache2 license)[https://github.com/neonbjb/tortoise-tts/blob/main/LICENSE]
# https://github.com/neonbjb/tortoise-tts/blob/main/tortoise/utils/text.py
def split_and_recombine_text(
    text: str, desired_length: int = 200, max_length: int = 300
) -> list[str]:
    """Split text it into chunks of a desired length trying to keep sentences intact."""
    # normalize text, remove redundant whitespace and convert non-ascii quotes to ascii
    text = re.sub(r"\n\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[“”]", '"', text)

    rv = []
    in_quote = False
    current = ""
    split_pos: list[int] = []
    pos = -1
    end_pos = len(text) - 1

    def seek(delta: int) -> str:
        nonlocal pos, in_quote, current
        is_neg = delta < 0
        for _ in range(abs(delta)):
            if is_neg:
                pos -= 1
                current = current[:-1]
            else:
                pos += 1
                current += text[pos]
            if text[pos] == '"':
                in_quote = not in_quote
        return text[pos]

    def peek(delta: int) -> str:
        p = pos + delta
        return text[p] if p < end_pos and p >= 0 else ""

    def commit() -> None:
        nonlocal rv, current, split_pos
        rv.append(current)
        current = ""
        split_pos = []

    while pos < end_pos:
        c = seek(1)
        # do we need to force a split?
        if len(current) >= max_length:
            if len(split_pos) > 0 and len(current) > (desired_length / 2):
                # we have at least one sentence and we are over half the desired length, seek back to the last split
                d = pos - split_pos[-1]
                seek(-d)
            else:
                # no full sentences, seek back until we are not in the middle of a word and split there
                while c not in "!?.\n " and pos > 0 and len(current) > desired_length:
                    c = seek(-1)
            commit()
        # check for sentence boundaries
        elif not in_quote and (c in "!?\n" or (c == "." and peek(1) in "\n ")):
            # seek forward if we have consecutive boundary markers but still within the max length
            while (
                pos < len(text) - 1 and len(current) < max_length and peek(1) in "!?."
            ):
                c = seek(1)
            split_pos.append(pos)
            if len(current) >= desired_length:
                commit()
        # treat end of quote as a boundary if its followed by a space or newline
        elif in_quote and peek(1) == '"' and peek(2) in "\n ":
            seek(2)
            split_pos.append(pos)
    rv.append(current)

    # clean up, remove lines with only whitespace or punctuation
    rv = [s.strip() for s in rv]
    return [s for s in rv if len(s) > 0 and not re.match(r"^[\s\.,;:!?]*$", s)]


if __name__ == "__main__":
    typer.run(main)
