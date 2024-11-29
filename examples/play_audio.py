import numpy as np

def wave_gen(freq,sample_rate,length):
    dt = 1/sample_rate
    t = np.arange(0, length, dt,dtype=np.float32)
    mono = np.sin(2*np.pi*freq*t) * np.exp(-t*5)
    stereo = np.zeros((len(mono)*2,), dtype=np.float32)
    stereo[0::2] = mono
    stereo[1::2] = mono
    return stereo.tobytes()

import sdl3_audio.audio as audio
audio._init_library("./SDL3-3.1.6-VC.dll")

spec = audio.AudioSpec("F32LE",sample_rate=48000)
dev = audio.open_default_playback_device(spec)
print(dev)
print(dev.spec)
stream = audio.AudioStream(dev)
audio1 = audio.Audio.from_buffer(wave_gen(880,48000,1), spec)
audio2 = audio.Audio.from_buffer(wave_gen(440,48000,1), spec)
audio3 = audio.Audio.from_wav_file("./resources/sample.wav").convert(spec)

stream.put_audio(audio1)
stream.put_audio(audio2)
stream.put_audio(audio3)


while stream.queued_data_length()>0:
    pass
while stream.available_data_length()>0:
    pass


