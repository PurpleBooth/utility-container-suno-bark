from src.main import count_syllables_in_phrase_roughly, pre_process_text, split_phrase


def test_short_sentence_become_a_single_phrase() -> None:
    assert pre_process_text("Hello, world!") == ["Hello, world!"]


def test_multiple_short_phrases_become_one() -> None:
    assert pre_process_text(
        "Hello, world! Hello, world! Hello, world! Hello, world!"
    ) == ["Hello, world! Hello, world! Hello, world! Hello, world!"]


def test_multiple_long_single_senence_phrases_become_two() -> None:
    assert pre_process_text(
        "As he crossed toward the pharmacy at the corner he involuntarily turned his head because of a burst of light that had ricocheted from his temple, and saw, with that quick smile with which we greet a rainbow or a rose, a blindingly white parallelogram of sky being unloaded from the van—a dresser with mirrors across which, as across a cinema screen, passed a flawlessly clear reflection of boughs sliding and swaying not arboreally, but with a human vacillation, produced by the nature of those who were carrying this sky, these boughs, this gliding facade."
    ) == [
        "As he crossed toward the pharmacy at the corner he involuntarily turned his "
        "head because of a burst",
        "of light that had ricocheted from his temple, and saw, with that quick smile "
        "with which we greet a rainbow or a rose, a",
        "blindingly white parallelogram of sky being unloaded from the van—a dresser "
        "with mirrors across which, as across",
        "a cinema screen, passed a flawlessly clear reflection of boughs sliding and "
        "swaying not arboreally, but with a human",
        "vacillation, produced by the nature of those who were carrying this sky, "
        "these boughs, this gliding facade.",
    ]


def test_split_phrase_trims_whitespace() -> None:
    assert split_phrase("  abc  ") == ["abc"]


def test_count_sylables_in_phrase_roughly() -> None:
    assert count_syllables_in_phrase_roughly("Hello, world!") == 3
