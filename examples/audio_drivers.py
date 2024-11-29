import os

# Uncomment one line to specify a driver
# os.environ["SDL_AUDIO_DRIVER"]="wasapi"
# os.environ["SDL_AUDIO_DRIVER"]="directsound"
# os.environ["SDL_AUDIO_DRIVER"]="disk"
# os.environ["SDL_AUDIO_DRIVER"]="dummy"

import sdl3_audio.audio as audio
audio._init_library("./SDL3-3.1.6-VC.dll")

print("Available audio drivers:")
for drv in audio.list_audio_drivers():
    print(drv)
print()

print("Current audio driver:")
print(audio.get_current_audio_driver())
print()

