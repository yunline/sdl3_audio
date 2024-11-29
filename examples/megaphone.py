import sdl3_audio.audio as audio
audio._init_library("./SDL3-3.1.6-VC.dll")

playback_dev = audio.open_default_playback_device()
recording_dev = audio.open_default_recording_device()
print(playback_dev)
print(playback_dev.spec)
print(recording_dev)
print(recording_dev.spec)

stream_recording = audio.AudioStream(recording_dev)
stream_palyback = audio.AudioStream(playback_dev, src_spec=recording_dev.spec)

stream_palyback.gain = audio.dB(+10)

while 1:
    # wait for data from recording stream
    tmp_audio = stream_recording.get_audio()
    
    # feed the data to the playback stream
    stream_palyback.put_audio(tmp_audio)

