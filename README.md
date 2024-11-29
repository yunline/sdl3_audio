# Pygame-ce New Audio Module Prototype

Powered by SDL3 and ctypes interface.

## Install
```shell
pip install .
```

## Use
```py
# Import library and load dll
import sdl3_audio.audio as audio
audio._init_library("./SDL3-3.1.6-VC.dll")
# SDL3 dll is not provided in this repository
# You can get it from https://github.com/libsdl-org/SDL/releases/tag/preview-3.1.6

# Open the default playback device
dev = audio.open_default_playback_device(spec)

# Create a stream binding to the device
stream = audio.AudioStream(dev)

# Load a piece wav audio
# Convert it to the format of the stream
au = audio.Audio.from_wav_file("./resources/sample.wav").convert(stream.src_spec)

# Put the audio into the stream
stream.put_audio(au)

# Wait for play end
while stream.queued_data_length()>0:
    pass

```
See [examples]() directory for more example of usages.

## Docs
WIP


