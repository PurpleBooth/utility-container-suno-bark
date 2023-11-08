# utility-container-suno-bark

A container for generating speech from text.

## Usage

```
Usage: main.py [OPTIONS] SOURCE_TEXT_FILE DESTINATION_WAV_FILE [VOICE_PROMPT]

Arguments:
  SOURCE_TEXT_FILE      Text file to use as source for generation, could be a
                        file path or url  [required]
  DESTINATION_WAV_FILE  [required]
  [VOICE_PROMPT]        This is used to create an initial phrase that will
                        generate the voice of the speaker.  [default: This is
                        being recorded in a studio.]

Options:
  --help  Show this message and exit.
```

Models are downloaded to /cache, so you may want to mount that as a volume.