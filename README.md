# utility-container-suno-bark

A container for generating speech from text.

## Usage

```yaml
Usage: main.py [OPTIONS] SOURCE_TEXT_FILE DESTINATION_WAV_FILE

Arguments:
  SOURCE_TEXT_FILE      [required]
  DESTINATION_WAV_FILE  [required]

Options:
  --help  Show this message and exit.
```

Models are downloaded to /cache, so you may want to mount that as a volume.