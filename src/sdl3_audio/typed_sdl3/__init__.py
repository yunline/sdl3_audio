# This file is auto generated
import ctypes
import typing

SDL_PropertiesID:typing.TypeAlias=ctypes.c_uint32

class SDL_Semaphore(ctypes.Structure):
    _fields_ = [ # type: ignore
    ]

SDL_AudioDeviceID:typing.TypeAlias=ctypes.c_uint32
SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK=SDL_AudioDeviceID(4294967295)
SDL_AUDIO_DEVICE_DEFAULT_RECORDING=SDL_AudioDeviceID(4294967294)
SDL_AudioFormat:typing.TypeAlias=ctypes.c_uint16
SDL_AUDIO_UNKNOWN=SDL_AudioFormat(0)
SDL_AUDIO_U8=SDL_AudioFormat(8)
SDL_AUDIO_S8=SDL_AudioFormat(32776)
SDL_AUDIO_S16LE=SDL_AudioFormat(32784)
SDL_AUDIO_S16BE=SDL_AudioFormat(36880)
SDL_AUDIO_S32LE=SDL_AudioFormat(32800)
SDL_AUDIO_S32BE=SDL_AudioFormat(36896)
SDL_AUDIO_F32LE=SDL_AudioFormat(33056)
SDL_AUDIO_F32BE=SDL_AudioFormat(37152)

class SDL_AudioSpec(ctypes.Structure):
    format:int
    channels:int
    freq:int
    _fields_ = [ # type: ignore
        ("format",SDL_AudioFormat),
        ("channels",ctypes.c_int),
        ("freq",ctypes.c_int),
    ]


class SDL_AudioStream(ctypes.Structure):
    _fields_ = [ # type: ignore
    ]

if typing.TYPE_CHECKING:
    SDL_AudioStreamCallback:typing.TypeAlias=ctypes._FuncPointer
else:
    SDL_AudioStreamCallback=ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(SDL_AudioStream), ctypes.c_int, ctypes.c_int)
SDL_InitFlags:typing.TypeAlias=ctypes.c_uint32
SDL_INIT_AUDIO=SDL_InitFlags(16)

def load_sdl3_dll(sdl_dll_path):
    sdl3 = ctypes.cdll.LoadLibrary(sdl_dll_path)
    sdl3.SDL_SetPointerProperty.restype = ctypes.c_bool
    sdl3.SDL_GetPointerProperty.restype = ctypes.POINTER(None)
    sdl3.SDL_CreateSemaphore.restype = ctypes.POINTER(SDL_Semaphore)
    sdl3.SDL_WaitSemaphoreTimeout.restype = ctypes.c_bool
    sdl3.SDL_GetSemaphoreValue.restype = ctypes.c_uint32
    sdl3.SDL_GetNumAudioDrivers.restype = ctypes.c_int
    sdl3.SDL_GetAudioDriver.restype = ctypes.c_char_p
    sdl3.SDL_GetCurrentAudioDriver.restype = ctypes.c_char_p
    sdl3.SDL_GetAudioRecordingDevices.restype = ctypes.POINTER(SDL_AudioDeviceID)
    sdl3.SDL_GetAudioPlaybackDevices.restype = ctypes.POINTER(SDL_AudioDeviceID)
    sdl3.SDL_GetAudioDeviceName.restype = ctypes.c_char_p
    sdl3.SDL_GetAudioDeviceFormat.restype = ctypes.c_bool
    sdl3.SDL_OpenAudioDevice.restype = SDL_AudioDeviceID
    sdl3.SDL_PauseAudioDevice.restype = ctypes.c_bool
    sdl3.SDL_ResumeAudioDevice.restype = ctypes.c_bool
    sdl3.SDL_AudioDevicePaused.restype = ctypes.c_bool
    sdl3.SDL_GetAudioDeviceGain.restype = ctypes.c_float
    sdl3.SDL_SetAudioDeviceGain.restype = ctypes.c_bool
    sdl3.SDL_BindAudioStream.restype = ctypes.c_bool
    sdl3.SDL_GetAudioStreamDevice.restype = SDL_AudioDeviceID
    sdl3.SDL_CreateAudioStream.restype = ctypes.POINTER(SDL_AudioStream)
    sdl3.SDL_GetAudioStreamProperties.restype = SDL_PropertiesID
    sdl3.SDL_GetAudioStreamFormat.restype = ctypes.c_bool
    sdl3.SDL_SetAudioStreamFormat.restype = ctypes.c_bool
    sdl3.SDL_GetAudioStreamGain.restype = ctypes.c_float
    sdl3.SDL_SetAudioStreamGain.restype = ctypes.c_bool
    sdl3.SDL_GetAudioStreamFrequencyRatio.restype = ctypes.c_float
    sdl3.SDL_SetAudioStreamFrequencyRatio.restype = ctypes.c_bool
    sdl3.SDL_PutAudioStreamData.restype = ctypes.c_bool
    sdl3.SDL_GetAudioStreamData.restype = ctypes.c_int
    sdl3.SDL_GetAudioStreamAvailable.restype = ctypes.c_int
    sdl3.SDL_GetAudioStreamQueued.restype = ctypes.c_int
    sdl3.SDL_FlushAudioStream.restype = ctypes.c_bool
    sdl3.SDL_ClearAudioStream.restype = ctypes.c_bool
    sdl3.SDL_SetAudioStreamGetCallback.restype = ctypes.c_bool
    sdl3.SDL_SetAudioStreamPutCallback.restype = ctypes.c_bool
    sdl3.SDL_LoadWAV.restype = ctypes.c_bool
    sdl3.SDL_MixAudio.restype = ctypes.c_bool
    sdl3.SDL_ConvertAudioSamples.restype = ctypes.c_bool
    sdl3.SDL_GetError.restype = ctypes.c_char_p
    sdl3.SDL_Init.restype = ctypes.c_bool
    sdl3.SDL_WasInit.restype = SDL_InitFlags

    return sdl3
